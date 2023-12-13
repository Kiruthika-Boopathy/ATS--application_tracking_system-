from django.db import models

class UserDetails(models.Model):
    user_email = models.CharField(db_column='User_Email', primary_key=True, max_length=100)  # Field name made lowercase.
    source = models.CharField(db_column='Source', max_length=100, blank=True, null=True)  # Field name made lowercase.
    source_ids = models.CharField(db_column='Source_IDS', max_length=100, blank=True, null=True)  # Field name made lowercase.
    subject = models.CharField(db_column='Subject', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User_details'
