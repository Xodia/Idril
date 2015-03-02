# -*- coding: utf8 -*-

from __future__ import unicode_literals
import time
import datetime
from datetime import date

# import models from applications
from base.models import Permission, Media, Achievement, News
from member.models import User, Address, PersonnalInformation
from forum.models import Category, Topic, Message
from project.models import ProjectCategory, Project, Gift, Funding

from faker import Factory

# FLUSH DATABASE
Funding.objects.all().delete()
Project.objects.all().delete()
PersonnalInformation.objects.all().delete()
User.objects.all().delete()
Address.objects.all().delete()
Category.objects.all().delete()
Topic.objects.all().delete()
Message.objects.all().delete()
ProjectCategory.objects.all().delete()
Gift.objects.all().delete()
Permission.objects.all().delete()
Media.objects.all().delete()

# ------------------- BASE -------------------

# PERMISSION
permission1 = Permission.objects.create(name="ADMIN")
permission2 = Permission.objects.create(name="USER")
permission3 = Permission.objects.create(name="ALL")
print "\nPermissions created"

# MEDIA
media1 = Media.objects.create(name="Avatar1", date=date.today())
media2 = Media.objects.create(name="Avatar2", date=date.today())
media3 = Media.objects.create(name="Illustr1", date=date.today())
print "\nMedias created"

# ACHIEVEMENT
achievement1 = Achievement.objects.create(name="Achievement1",
                                          description="Achievement descr")
print "\nAchievements created"

# ------------------- MEMBER -------------------

# USER
user1 = User.objects.create(first_name="Allan", last_name="HOUSSOULLIEZ",
                            password="allan",
                            username="allan",
                            email="allan.houssoulliez@epitech.eu")

user2 = User.objects.create(first_name="Michael", last_name="BRAVO",
                            password="michael",
                            username="michael",
                            email="michael.bravo@gmail.com")

user3 = User.objects.create(first_name="Jean", last_name="MARC",
                            password="jean",
                            username="jean",
                            email="jean.marc@epitech.eu")

fake = Factory.create('fr_FR')
for i in range(0, 2):
    User.objects.create(first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        password=fake.catch_phrase_noun(),
                        username=fake.department_name(),
                        email=fake.free_email())

print "\nUsers created"

# ADDRESS
address1 = Address.objects.create(street1="9 rue de Thiancourt",
                                  zip_code="90100", city="Delle",
                                  phone_number1="0631759965", user=user1)
address2 = Address.objects.create(street1="2 rue de l'ecole",
                                  zip_code="67000", city="Strasbourg",
                                  phone_number1="0622359911", user=user2)
address3 = Address.objects.create(street1="10 avenue des ecoliers",
                                  zip_code="75000", city="Paris",
                                  phone_number1="0645732965", user=user3)
print "\nAddresses created"

# PERSONNALINFORMATION
personnalInformation1 = PersonnalInformation.objects.create(
    credit_card_number="2345324598652351",
    credit_card_expiration_date="2014-11-21",
    user=user2)
print "\nPersonal information created"

# ------------------- BASE -------------------

# NEWS
news1 = News.objects.create(title="news1", content="Content news1",
                            date=date.today(), user=user1)
print "\nNews created"

# ------------------- FORUM -------------------

# FORUMCATEGORY
category1 = Category.objects.create(title="Projet",
                                         description="Categorie projet")
print "\nForum Categories created"

# TOPIC
topic1 = Topic.objects.create(title="Probleme pour poster un projet",
                              author=user2)

topic2 = Topic.objects.create(title="Comment financer un projet ?",
                              author=user1)

topic3 = Topic.objects.create(title="Suppression de compte",
                              author=user1)

topic4 = Topic.objects.create(title="Messagerie",
                              author=user3)

topic5 = Topic.objects.create(title="Modification de profil",
                              author=user3)
print "\nForum Topics created"

# FORUMMESSAGE
message1 = Message.objects.create(content="Je n'arrive pas a poster mon projet... erreur d'authenfication !", author=user2, topic=topic1)
message2 = Message.objects.create(content="Arrives-tu a consulter des projets ?", author=user1, topic=topic1)
message3 = Message.objects.create(content="Oui je peux consulter des projets !", author=user2, topic=topic1)
message4 = Message.objects.create(content="Je ne comprends pas, desole...", author=user1, topic=topic1)

message5 = Message.objects.create(content="Bonjour, comment puis-je financer un projet ?", author=user3, topic=topic2)
message6 = Message.objects.create(content="Tu peux financer un projet via PayPal ou directement avec une carte bancaire.", author=user2, topic=topic2)
message7 = Message.objects.create(content="Merci beaucoup !", author=user3, topic=topic2)

message8 = Message.objects.create(content="Arrivez-vous a supprimer votre compte ?", author=user1, topic=topic3)
message9 = Message.objects.create(content="Oui, tableau de bord -> Suppression de compte.", author=user2, topic=topic3)

message10 = Message.objects.create(content="Test messagerie", author=user2, topic=topic4)
message11 = Message.objects.create(content="La messagerie fonctionne !", author=user1, topic=topic4)
message12 = Message.objects.create(content="Cool", author=user3, topic=topic4)

message13 = Message.objects.create(content="L'edition de profil est OK pour vous !?", author=user1, topic=topic5)
message14 = Message.objects.create(content="OUI OUI !", author=user2, topic=topic5)
print "\nForum Messages created"

# ------------------- PROJECT -------------------

# PROJECTCATEGORY
project_category1 = ProjectCategory.objects.create(
    name="Catastrophes naturelles",
    description="Inondations, tremblements de terre, etc...")
project_category2 = ProjectCategory.objects.create(
    name="Aide a la construction",
    description="Construction d'ecoles, d'hopitaux, etc...")
print "\nProject Categories created"

# GIFT
gift1 = Gift.objects.create(name="Porte clefs",
                            description="Un porte clefs personalise",
                            amount_required="20.00")
gift2 = Gift.objects.create(name="Billet d'avion",
                            description="Un billet d'avion pour aller aider "
                            "les sinistres", amount_required="2500.00",
                            max_amount=10)
print "\nProject Gifts created"

# PROJECT
project1 = Project.objects.create(title="Tsunami",
                                  content="Aidez-nous pour le tsunami !",
                                  date=date.today(),
                                  amount_required="40000.00",
                                  amount_actual="2540.00",
                                  category=project_category1,
                                  end_date=datetime.date.today() + datetime.timedelta(days=60),
                                  user=user2)
project1.gifts.add(gift1)
project1.gifts.add(gift2)
project1.save()
print "\nProjects created"

# FUNDING
funding1 = Funding.objects.create(date=date.today(), amount="20.00",
                                  user=user2, project=project1, gift=gift1)
funding2 = Funding.objects.create(date=date.today(), amount="2500.00",
                                  user=user1, project=project1, gift=gift2)
funding3 = Funding.objects.create(date=date.today(), amount="20.00",
                                  user=user1, project=project1, gift=gift1)
print "\nProject Fundings created"
