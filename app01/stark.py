

from stark.service.stark import site,ModelStark

from django.urls import reverse
from .models import *


from django.utils.safestring import mark_safe

from django.forms import ModelForm
from django.forms import widgets as wid


class BookModelForm(ModelForm):
    class Meta:
        model = Book
        fields = "__all__"

        labels={
            "title":"书籍名称",
            "price":"价格"
        }

class BookConfig(ModelStark):
    list_display = ["title","price","publishDate"]
    modelform_class=BookModelForm


site.register(Book,BookConfig)






site.register(Publish)
site.register(Author)
site.register(AuthorDetail)






