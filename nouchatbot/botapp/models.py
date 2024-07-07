from django.db import models

class users(models.Model):
    uid = models.CharField(max_length=50, null=False)
    question = models.CharField(max_length=250, null=False)
    asktime = models.DateTimeField(auto_now=True)
    resSF = models.CharField(max_length=2, null=True)
    restext = models.CharField(max_length=10, null=True)
    
    def __str__(self):
        return self.uid