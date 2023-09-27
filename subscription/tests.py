import datetime
import itertools

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from base_tests import BaseTestCase
from .models import Plan, Subscription
from .serializers import PlanSerializer


class SubscriptionTests(BaseTestCase):
    tomorrow = None
    yesterday = None
    day = None
    date = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.date = timezone.now()
        cls.day = datetime.timedelta(days=1)
        cls.yesterday = cls.date - cls.day
        cls.tomorrow = cls.date + cls.day
        cls.permutations = itertools.product((cls.yesterday, cls.tomorrow, None), repeat=2)

    @staticmethod
    def create_plan(start_date=None, end_date=None):
        return Plan.objects.create(
            title='1d',
            description='1d',
            start_date=start_date,
            end_date=end_date,
            price=50,
            duration=1
        )

    def create_sub(self):
        plan = self.create_plan()
        response = self.client.post(reverse('plan-buy', kwargs={'pk': plan.pk}))
        return plan, response

    def test_get_list_active_plans(self):
        self.switch_user('user1')

        for start_date, end_date in self.permutations:
            if start_date and end_date and start_date > end_date:
                plan = self.create_plan(start_date=start_date, end_date=end_date)
                serializer = PlanSerializer(plan)

                list_response = self.client.get(reverse('plan-list'))
                detail_response = self.client.get(reverse('plan-detail', kwargs={'pk': plan.pk}))

                if start_date and start_date > self.date or end_date and end_date < self.date:
                    self.assertNotIn(serializer.data, list_response.json())
                    self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)
                else:
                    self.assertIn(serializer.data, list_response.json())
                    self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

    def test_validation_plan(self):
        for start_date, end_date in self.permutations:
            plan = self.create_plan(start_date=start_date, end_date=end_date)

            if (
                    start_date and end_date and start_date > end_date or
                    start_date and start_date < self.date or
                    end_date and end_date < self.date
            ):
                with self.assertRaises(ValidationError):
                    plan.full_clean()
            else:
                plan.full_clean()

    def test_sub_buy(self):
        self.switch_user('user1')

        plan, response = self.create_sub()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        r_json = response.json()
        self.assertEqual(r_json['purchase_price'], plan.price)
        self.assertEqual(r_json['plan'], plan.id)

        plan.is_active = False
        plan.save()

        response = self.client.post(reverse('plan-buy', kwargs={'pk': plan.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_sub(self):
        self.switch_user('user1')

        plan, response_cr_sub = self.create_sub()

        sub_id = response_cr_sub.json()['id']

        response = self.client.get(reverse('active-subscription'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], sub_id)

        Subscription.objects.get(id=sub_id).delete()

        response = self.client.get(reverse('active-subscription'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
