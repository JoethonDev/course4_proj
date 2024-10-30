from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
import urllib.parse

# Celery Import
from celery.exceptions import TimeoutError
from course4_proj.celery import app

# Models
from movies.models import SearchTerm, Genre, Movie
from movies.tasks import search_and_save


# Create your views here.
def search_view(request):
  # Get Search from query paramters
  search_term = request.GET.get("search_term")
  response = search_and_save.delay(search_term)
  print(response.id)
  # Try to get Results
  try:
    results = response.get(timeout=2)

  except TimeoutError:
    print("Timeout Occur")
    return redirect(
      reverse("wait-view", args=(response.id, )) + f"?search_term={urllib.parse.quote_plus(search_term)}"
    )
  
  return redirect(
    reverse("result-view") + f"?search_term={urllib.parse.quote_plus(search_term)}"
  )

def wait_view(request, task_id):
  # Task ID
  # task_id = request.GET.get("task-id")
  search_term = request.GET.get("search_term")

  # Try to get Results
  try:
    response = app.AsyncResult(task_id)
    results = response.get(-1)

  except TimeoutError:
    return HttpResponse("<h1>Please Refresh Page!</h1>")

  return redirect(
    reverse("result-view") + f"?search_term={urllib.parse.quote_plus(search_term)}"
  )

def result_view(request):
  search_term = request.GET.get("search_term")
  movies =  Movie.objects.filter(title__icontains=search_term)
  return HttpResponse(
        "\n".join([movie.title for movie in movies]), content_type="text/plain"
    )
