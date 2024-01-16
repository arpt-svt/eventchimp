from django.db import models
from django.utils.text import slugify
from django.conf import settings

from commons.utils import generate_random_string


class Event(models.Model):
    organiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    duration_in_minutes = models.PositiveIntegerField(default=60)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    step_in_min = models.PositiveIntegerField(default=60)
    rolling_days = models.PositiveIntegerField(null=True, blank=True)
    before_buffer_time_in_minutes = models.PositiveIntegerField(default=0)
    after_buffer_time_in_minutes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['organiser', 'slug']

    def get_owner_id(self):
        return self.organiser_id

    def soft_delete(self):
        self.is_active = False
        self.save(
            force_update=True,
            update_fields=["is_active", "updated_at"]
        )

    def generate_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        i = 1
        while Event.objects.filter(organiser=self.organiser_id, slug=slug).exists():
            slug = f"{base_slug}-{i}{generate_random_string(6)}"
            i += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)
