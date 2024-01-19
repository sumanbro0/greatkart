# Generated by Django 5.0.1 on 2024-01-19 15:00

from django.db import migrations


def delete_duplicate_reviews(apps, schema_editor):
    Review = apps.get_model('product', 'Review')
    for product in Review.objects.values_list('product', flat=True).distinct():
        user_ids = []
        for review in Review.objects.filter(product=product).order_by('id'):
            if review.user_id in user_ids:
                review.delete()
            else:
                user_ids.append(review.user_id)


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
                migrations.RunPython(delete_duplicate_reviews),

    ]
