from django.db import models

class Street(models.Model):
	""" Representation of a Street in Chicago """
	STREET_TYPES = (
		("st", "Street"),
		("av", "Avenue"),
		("blvd", "Boulevard"),
		("rd", "Road"),
	)

	STREET_DIRECTIONS = (
		("n", "North"),
		("e", "East"),
		("s", "South"),
		("w", "West"),
	)

	street_number = models.IntegerField()
	street_direction = models.CharField(max_length=1, choices=STREET_DIRECTIONS)
	street_type = models.CharField(max_length=20, choices=STREET_TYPES)
	street_name = models.CharField(max_length=255)

class Participant(models.Model):
	""" Representation of a person who can participate in a Event """
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	phone_number = models.IntegerField()
	email = models.EmailField()
	street = models.ForeignKey(Street)

class Event(models.Model):

	name = models.CharField(max_length=255)
	date = models.DateTimeField()
	site = models.CharField(max_length=255)
	street = models.ForeignKey(Street)
	participants = models.ManyToManyField(Participant)
