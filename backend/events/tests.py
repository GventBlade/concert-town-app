from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import Event

User = get_user_model()


class EventListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="organizer@example.com",
            password="Password123!",
        )

        self.event1 = Event.objects.create(
            title="Concert A",
            description="Description A",
            date="2026-08-01T19:00:00Z",
            location="Kyiv",
            price="50.00",
            total_seats=100,
            available_seats=100,
            organizer=self.user,
        )
        self.event2 = Event.objects.create(
            title="Concert B",
            description="Description B",
            date="2026-08-02T19:00:00Z",
            location="Odesa",
            price="30.00",
            total_seats=50,
            available_seats=50,
            organizer=self.user,
        )
        self.url = reverse("event-list")

    def test_get_events_list_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_events_pagination_structure(self):
        response = self.client.get(self.url)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_events_by_organizer(self):
        other_user = User.objects.create_user(
            email="other-organizer@example.com",
            password="Password123!",
        )
        Event.objects.create(
            title="Concert C",
            description="Description C",
            date="2026-08-03T19:00:00Z",
            location="Lviv",
            price="40.00",
            total_seats=75,
            available_seats=75,
            organizer=other_user,
        )

        response = self.client.get(self.url, {"organizer": other_user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Concert C")
