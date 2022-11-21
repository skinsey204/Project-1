import random
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from markdown2 import Markdown
from . import util

class SearchForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
      "class": "search",
      "placeholder": "Search Logicipedia"}))

class CreateForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
      "placeholder": "Entry Title"}))
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
      "placeholder": "Enter Entry Content using Github Markdown"
    }))

class EditForm(forms.Form):
  text = forms.CharField(label='', widget=forms.Textarea(attrs={
      "placeholder": "Enter Entry Content using Github Markdown"
    }))


def index(request):
    """ Home Page on Site, displays all available entries """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm(),
    })

def entry(request, title):

    entry_md = util.get_entry(title)

    if entry_md != None:
        # pull up the entry if it exists
        entry_HTML = Markdown().convert(entry_md)
        return render(request, "encyclopedia/entry.html", {
          "title": title,
          "entry": entry_HTML,
          "search_form": SearchForm(),
          })
    else:
        # look for similar results
        util.similar_search = util.similar_search(title)

        return render(request, "encyclopedia/error.html", {
          "title": title,
          "similar_search": util.similar_search,
          "search_form": SearchForm(),
          })

def search(request):

    # if they enter in the searchbar
    if request.method == "POST":
        form = SearchForm(request.POST)

        # if what they entered is okay, search it
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry_md = util.get_entry(title)

            print('search request: ', title)

            if entry_md:
                # show the entry they searched for
                return redirect(reverse('entry', args=[title]))
            else:
                # show the similar searches
                similar_search = util.similar_search(title)

                return render(request, "encyclopedia/search.html", {
                "title": title,
                "similar_search": similar_search,
                "search_form": SearchForm()
                })

    # if all else fails, get back to home page
    return redirect(reverse('index'))

def create(request):

    # If reached by clicking on the create link, display the create form:
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
          "create_form": CreateForm(),
          "search_form": SearchForm()
        })

    # Otherwise if reached by form submission:
    elif request.method == "POST":
        form = CreateForm(request.POST)

        # If form is valid, process the form:
        if form.is_valid():
          title = form.cleaned_data['title']
          text = form.cleaned_data['text']
        else:
          messages.error(request, 'Entry form not valid, please try again!')
          return render(request, "encyclopedia/create.html", {
            "create_form": form,
            "search_form": SearchForm()
          })

        # Check that title does not already exist:
        if util.get_entry(title):
            messages.error(request, f'This entry title already exists. If you feel the entry "{title}" is missing information, please edit the entry instead.')
            return render(request, "encyclopedia/create.html", {
              "create_form": form,
              "search_form": SearchForm()
            })
        # Otherwise save new entry and display it:
        else:
            util.save_entry(title, text)
            messages.success(request, f'New page "{title}" created successfully!')
            return redirect(reverse('entry', args=[title]))

def edit(request, title):

    # If reached by clicking on the editing link, return the edit form:
    if request.method == "GET":
        text = util.get_entry(title)

        # If title does not exist, return this error:
        if text == None:
            messages.error(request, f'The entry for "{title}" does not exist. Please create an entry for "{title}" if you wish to edit it')

        # Otherwise return edit form with existing entry data:
        return render(request, "encyclopedia/edit.html", {
          "title": title,
          "edit_form": EditForm(initial={'text':text}),
          "search_form": SearchForm()
        })

    # If reached via posting form, updated page and redirect to page:
    elif request.method == "POST":
        form = EditForm(request.POST)

        if form.is_valid():
          text = form.cleaned_data['text']
          util.save_entry(title, text)
          messages.success(request, f'Entry "{title}" updated successfully!')
          return redirect(reverse('entry', args=[title]))

        else:
          messages.error(request, f'Editing form not valid, please try again!')
          return render(request, "encyclopedia/edit.html", {
            "title": title,
            "edit_form": form,
            "search_form": SearchForm()
          })

def random_entry(request):
  
    # randomly choose a title from the list:
    titles = util.list_entries()
    title = random.choice(titles)

    # go to that page
    return redirect(reverse('entry', args=[title]))