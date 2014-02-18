from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.mail import send_mail

from dbe.shared.utils import *

notify = False

#BaseModels is abstract class
class Post(BaseModel):
    title = CharField(max_length = 60)
    body = TextField()
    created = DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering = ["-created"]
        
    def __unicode__(self):
        return self.title

class Comment(BaseModel):
    author = CharField(max_length=60, blank = True)
    body = TextField()
    post = ForeignKey(Post, related_name="comments", blank = True, null = True)
    created = DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        return u"%s: %s" % (self.post, self.body[:60])

    def save(self, *args, **kwargs):
        if notify:
            tpl            = "Comment was was added to '%s' by '%s': \n\n%s"
            message        = tpl % (self.post, self.author, self.body)
            from_addr      = "1991.daiki@gmail.com"
            recipient_list = ["1991.daiki@gmail.com"]

            send_mail("New comment added", message, from_addr, recipient_list)
        super(Comment, self).save(*args, **kwargs)
