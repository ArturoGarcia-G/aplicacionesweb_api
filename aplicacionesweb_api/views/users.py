from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from aplicacionesweb_api.serializers import *
from aplicacionesweb_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json

class UsersAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        profiles = Profiles.objects.filter(user__is_active = 1).order_by("id")
        lista = ProfilesSerializer(profiles, many=True).data
        
        return Response(lista, 200)

class UsersView(generics.CreateAPIView):
    #Obtener usuario por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(Profiles, id = request.GET.get("id"))
        user = ProfilesSerializer(user, many=False).data

        return Response(user, 200)
    
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = 'user'
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Create a profile for the user
            profile = Profiles.objects.create(user=user,
                                              matricula= request.data["matricula"],
                                              curp= request.data["curp"].upper(),
                                              rfc= request.data["rfc"].upper(),
                                              fecha_nacimiento= request.data["fecha_nacimiento"],
                                              edad= request.data["edad"],
                                              telefono= request.data["telefono"],
                                              ocupacion= request.data["ocupacion"])
            profile.save()

            return Response({"profile_created_id": profile.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UsersViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
        profile = get_object_or_404(Profiles, id=request.data["id"])
        profile.fecha_nacimiento = request.data["fecha_nacimiento"]
        profile.curp = request.data["curp"]
        profile.rfc = request.data["rfc"]
        profile.edad = request.data["edad"]
        profile.telefono = request.data["telefono"]
        profile.ocupacion = request.data["ocupacion"]
        profile.matricula = request.data["matricula"]
        profile.save()
        temp = profile.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()
        user = ProfilesSerializer(profile, many=False).data

        return Response(user,200)
    def delete(self, request, *args, **kwargs):
        profile = get_object_or_404(Profiles, id=request.GET.get("id"))
        try:
            profile.user.delete()
            return Response({"details":"Usuario eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)