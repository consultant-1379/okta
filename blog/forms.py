from django import forms
from .models import Comment



class SearchForm(forms.Form):
    query=forms.CharField()



class EmailPostForm(forms.Form): #form for sending E-mail
    name=forms.CharField(max_length=25)
    email=forms.EmailField(max_length=80)
    to=forms.EmailField(max_length=80)
    comment=forms.CharField(required=False,
            widget=forms.Textarea)


class CommentForm(forms.ModelForm):
         # form form making comments to posts
    class Meta:
        model=Comment
        fields=('name','email','body')
