# -*- coding: utf8 -*-

from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from forum.models import Topic
from forum.models import Message
from django.conf import settings
from forum.models import Like
from django.contrib.auth import get_user
from forum.forms import TopicFormCreate
from forum.forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.core.mail import send_mail

def home(request):
    topics = Topic.objects.all()
    topics_list = []
    for topic in topics:
        topic_info = {}
        topic_info['topic'] = topic
        topic_info['nb_messages'] = Message.objects.filter(topic=topic).count()
        topic_info['last_message'] = Message.objects.filter(topic=topic).order_by('-date')[0]
        topics_list.append(topic_info)
    return render(request, 'forum/forum.html', {'topics_list': topics_list})


@login_required
def create_topic(request):
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/forum/')
        topicForm = TopicFormCreate(request.POST)
        messageForm = MessageForm(request.POST)
        if topicForm.is_valid() and messageForm.is_valid():
            topic = topicForm.save(commit=False)
            topic.author = get_user(request)
            topic.save()
            message = messageForm.save(commit=False)
            message.author = get_user(request)
            message.topic = topic
            message.save()
            return HttpResponseRedirect('/forum/')
    else:
        topicForm = TopicFormCreate()
        messageForm = MessageForm()
    args = {}
    args.update(csrf(request))
    args['topicForm'] = topicForm
    args['messageForm'] = messageForm
    return render(request, 'forum/create_topic.html', args)


def topic(request, id):
    currentTopic = Topic.objects.get(id=id)
    messages = Message.objects.filter(topic=currentTopic)
    args = {}
    args.update(csrf(request))
    args['topic'] = currentTopic
    args['messages'] = messages
    args['messageForm'] = MessageForm()
    args['path'] = request.path
    return render(request, 'forum/topic.html', args)


@login_required
def post_message(request, id):
    currentTopic = Topic.objects.get(id=id)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/forum/')
        messageForm = MessageForm(request.POST)
        print messageForm.errors
        if messageForm.is_valid():
            message = messageForm.save(commit=False)
            message.author = get_user(request)
            message.topic = currentTopic
            message.save()
    return HttpResponseRedirect(request.path.replace('post_message', ''))

@login_required
def reply_message(request, id):
    message = Message.objects.filter(id=request.GET.get('message'))
    return HttpResponse(message)

def calculate_like(id_message):
    likes = Like.objects.filter(message=id_message, state='1').count()
    dislikes = Like.objects.filter(message=id_message, state='0').count()
    return likes - dislikes

@login_required
def like_message(request, id):
    id_message = request.GET.get('message')
    message = Message.objects.get(id=id_message)
    already_exist = Like.objects.filter(user=request.user, message=message)
    if already_exist.count() > 0:
        state = already_exist[0].state
        Like.objects.filter(user=request.user, message=message).delete()
        if state == '0':
            like = Like(user=request.user, message=message, state='1')
            like.save()
    else:
        like = Like(user=request.user, message=message, state='1')
        like.save()
    return HttpResponse(calculate_like(id_message))

@login_required
def dislike_message(request, id):
    id_message = request.GET.get('message')
    message = Message.objects.get(id=id_message)
    already_exist = Like.objects.filter(user=request.user, message=message)
    if already_exist.count() > 0:
        state = already_exist[0].state
        Like.objects.filter(user=request.user, message=message).delete()
        if state == '1':
            like = Like(user=request.user, message=message, state='0')
            like.save()       
    else:
        like = Like(user=request.user, message=message, state='0')
        like.save()
    return HttpResponse(calculate_like(id_message))

@login_required
def report_message(request, id):
    id_message = request.GET.get('message')
    message = Message.objects.get(id=id_message)
    reason = request.GET.get('reason')
    c = {
         'user': request.user,
         'author': message.author.username,
         'message': message.content,
         'messageId': message.id,
         'reason': reason,
        }
    subject = 'Message report'
    email = loader.render_to_string("forum/report_email.html", c)
    send_mail(subject, email, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
    print "Message de ", message.author.username, "signalé pour le motif suivant :", 
    return HttpResponse()
