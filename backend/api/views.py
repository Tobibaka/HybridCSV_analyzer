from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .models import Dataset, EquipmentRecord
from .serializers import (
    DatasetListSerializer, 
    DatasetDetailSerializer, 
    EquipmentRecordSerializer,
    UserSerializer,
    LoginSerializer
)
from .utils import parse_csv_data, calculate_summary, generate_pdf_report


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session authentication without CSRF enforcement."""
    
    def enforce_csrf(self, request):
        return  # Skip CSRF check


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """User login endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                })
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """User logout endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def current_user(request):
    """Get current authenticated user info."""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email
            }
        })
    return Response({'authenticated': False})


class DatasetListView(generics.ListAPIView):
    """List all datasets (last 5)."""
    
    serializer_class = DatasetListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Dataset.objects.all()[:5]


@method_decorator(csrf_exempt, name='dispatch')
class DatasetDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a specific dataset."""
    
    queryset = Dataset.objects.all()
    serializer_class = DatasetDetailSerializer
    permission_classes = [permissions.AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class UploadCSVView(APIView):
    """Handle CSV file upload."""
    
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            file = request.FILES['file']
            
            # Validate file type
            if not file.name.endswith('.csv'):
                return Response(
                    {'error': 'File must be a CSV'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse CSV
            df, error = parse_csv_data(file)
            if error:
                return Response(
                    {'error': f'Failed to parse CSV: {error}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate summary
            summary = calculate_summary(df)
            
            # Create dataset
            dataset_name = request.data.get('name', file.name.replace('.csv', ''))
            
            # Handle anonymous user
            uploaded_by = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                uploaded_by = request.user
            
            dataset = Dataset.objects.create(
                name=dataset_name,
                file_name=file.name,
                total_records=len(df),
                uploaded_by=uploaded_by
            )
            dataset.set_summary(summary)
            dataset.save()
            
            # Create equipment records
            records = []
            for _, row in df.iterrows():
                records.append(EquipmentRecord(
                    dataset=dataset,
                    equipment_name=row['Equipment Name'],
                    equipment_type=row['Type'],
                    flowrate=float(row['Flowrate']),
                    pressure=float(row['Pressure']),
                    temperature=float(row['Temperature'])
                ))
            EquipmentRecord.objects.bulk_create(records)
            
            # Maintain only last 5 datasets
            old_datasets = list(Dataset.objects.all()[5:])
            for old_ds in old_datasets:
                old_ds.delete()
            
            # Return response
            serializer = DatasetDetailSerializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            import traceback
            print(f"Upload error: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': f'Server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dataset_summary(request, pk):
    """Get summary statistics for a dataset."""
    try:
        dataset = Dataset.objects.get(pk=pk)
        summary = dataset.get_summary()
        summary['dataset_id'] = dataset.id
        summary['dataset_name'] = dataset.name
        summary['uploaded_at'] = dataset.uploaded_at
        return Response(summary)
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dataset_records(request, pk):
    """Get all equipment records for a dataset."""
    try:
        dataset = Dataset.objects.get(pk=pk)
        records = dataset.records.all()
        serializer = EquipmentRecordSerializer(records, many=True)
        return Response(serializer.data)
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def generate_report(request, pk):
    """Generate and download PDF report for a dataset."""
    try:
        dataset = Dataset.objects.get(pk=pk)
        records = dataset.records.all()
        
        pdf_buffer = generate_pdf_report(dataset, records)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{dataset.name}_report.pdf"'
        return response
        
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def api_health(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'message': 'Chemical Equipment Parameter Visualizer API is running'
    })
