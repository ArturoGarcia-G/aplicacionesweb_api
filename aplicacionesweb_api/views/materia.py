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

class MateriasAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        materias = Materia.objects.all()
        lista = MateriaSerializer(materias, many=True).data
        
        return Response(lista, 200)
        
class MateriaView(generics.CreateAPIView, generics.RetrieveAPIView):
    serializer_class = MateriaSerializer

    def get(self, request, *args, **kwargs):
        materia_id = kwargs.get("pk")
        materia = get_object_or_404(Materia, id=materia_id)
        materia_data = MateriaSerializer(materia).data
        return Response(materia_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = MateriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MateriaViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
        materia = get_object_or_404(Materia, id=request.data["id"])
        materia.nrc = request.data["nrc"]
        materia.nombre = request.data["nombre"]
        materia.seccion = request.data["seccion"]
        materia.dias = request.data["dias"]
        materia.horario_inicio = request.data["horario_inicio"]
        materia.horario_fin = request.data["horario_fin"]
        materia.salon = request.data["salon"]
        materia.programa = request.data["programa"]
        materia.save()
        mate = MateriaSerializer(materia, many=False).data

        return Response(mate,200)
    def delete(self, request, *args, **kwargs):
        materia_id = self.kwargs.get('id')
        materia = get_object_or_404(Materia, id=materia_id)
        materia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
            


