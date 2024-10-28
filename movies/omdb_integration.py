from omdb.django_client import get_client_from_settings
from movies.models import Genre, SearchTerm, Movie
from django.utils import timezone
from datetime import timedelta
import re
import logging

omdb_client = get_client_from_settings()
logger = logging.getLogger(__name__)



def get_or_create_genres(names):
  for name in names:
    yield Genre.objects.get_or_create(name=name)[0]


def fill_movie_details(movie):
  """
    Fetch a movie's full details from OMDb. Then, save it to the DB. If the movie already has a `full_record` this does
    nothing, so it's safe to call with any `Movie`.
  """
  if movie.is_full_record:
    logger.warning(
      "'%s' is already a full record.",
      movie.title,
    )
    return

  imdb_id = movie.imdb_id
  omdb_movie = omdb_client.get_by_imdb_id(imdb_id)

  movie.runtime_minutes = omdb_movie.runtime_minutes
  movie.plot = omdb_movie.plot
  movie.is_full_record = True

  movie.genres.clear()
  for genre in get_or_create_genres(omdb_movie.genres):
    movie.genres.add(genre)

  movie.save()



def search_and_save(term):
  """
  Perform a search for search_term against the API, but only if it hasn't been searched in the past 24 hours. Save
  each result to the local DB as a partial record.
  """
  normalized_search_term = re.sub(r"\s+", " ", term.lower())
  search_term, created = SearchTerm.objects.get_or_create(term=normalized_search_term)
  current_time = timezone.now()

  if not created and (current_time < search_term.last_search + timedelta(hours=24)):
    logger.warning(
      "Search for '%s' was performed in the past 24 hours so not searching again.",
      normalized_search_term,
    )
    return

  for omdb_movie in omdb_client.search(term):
    logger.info("Saving movie: '%s' / '%s'", omdb_movie.title, omdb_movie.imdb_id)
    
    movie, created = Movie.objects.get_or_create(
      imdb_id=omdb_movie.imdb_id,
      defaults={
        'title': omdb_movie.title,
        'year': omdb_movie.year
      }
    )

    if created:
      logger.info("Movie %s is created!", movie.title)
  
  search_term.save()
