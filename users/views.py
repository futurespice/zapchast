from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, PhoneVerificationSerializer, UserLoginSerializer, UserSerializer, \
    PasswordResetConfirmSerializer
from .models import CustomUser
from .utils import generate_token, send_sms, standardize_phone_number, is_valid_phone_number, mask_phone_number
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)


class UserRegistrationInitView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone', 'password'],
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description="User's phone number"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
                'user_type': openapi.Schema(type=openapi.TYPE_INTEGER,
                                            description="User type (1 for client, 2 for seller)", default=1),
            },
        ),
        responses={
            201: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            if CustomUser.objects.filter(phone=phone).exists():
                return Response({"error": "User with this phone number already exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            verification_code = generate_token()
            user = CustomUser.objects.create_user(
                username=phone,
                phone=phone,
                password=serializer.validated_data['password'],
                user_type=serializer.validated_data.get('user_type', 1),
                is_active=False,
                verification_code=verification_code
            )

            masked_phone = mask_phone_number(phone)
            message = f"Your verification code for ZapchastKG is: {verification_code}"

            logger.info(f"Attempting to send SMS to {masked_phone}")
            if send_sms(phone, message):
                logger.info(f"SMS sent successfully to {masked_phone}")
                return Response({
                    "message": f"Verification code sent to {masked_phone}",
                    "phone": masked_phone
                }, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Failed to send SMS to {masked_phone}")
                user.delete()
                return Response({"error": "Failed to send verification code"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning(f"Invalid registration data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationVerifyView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=PhoneVerificationSerializer,
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                'user_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'is_phone_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        ),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    def post(self, request):
        serializer = PhoneVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            verification_code = serializer.validated_data['verification_code']
            try:
                user = CustomUser.objects.get(phone=phone, verification_code=verification_code, is_active=False)
                user.is_phone_verified = True
                user.is_active = True
                user.verification_code = None
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Phone verified successfully. Registration complete.",
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "Invalid verification code or phone number"},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                'user_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'is_phone_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        ),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        user = CustomUser.objects.filter(phone=phone).first()
        if user and user.check_password(serializer.validated_data['password']):
            if not user.is_phone_verified:
                return Response({"error": "Phone number not verified"}, status=status.HTTP_400_BAD_REQUEST)
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone'],
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description="User's phone number"),
            },
        ),
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error",
        },
    )
    def post(self, request):
        try:
            phone = standardize_phone_number(request.data.get('phone'))
        except ValueError:
            return Response({"error": "Invalid phone number format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        token = generate_token()
        user.reset_password_token = token
        user.save()

        masked_phone = mask_phone_number(phone)
        message = f"Your password reset token for ZapchastKG is: {token}"
        if send_sms(phone, message):
            return Response({
                "message": f"Password reset token sent to {masked_phone}",
                "phone": masked_phone
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send SMS"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                user = CustomUser.objects.get(phone=phone, reset_password_token=token)
            except CustomUser.DoesNotExist:
                return Response({"error": "Invalid token or phone number"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                validate_password(new_password, user)
            except ValidationError as e:
                return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.reset_password_token = None
            user.save()

            return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'is_phone_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                ),
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'user_type': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'is_phone_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                ),
            ),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'user_type': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'is_phone_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                ),
            ),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user