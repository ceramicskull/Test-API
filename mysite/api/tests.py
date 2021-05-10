from django.test import TestCase
from . import views
from django.http import JsonResponse
from django.test import Client
from django.core.handlers.wsgi import WSGIRequest
import json
# Create your tests here.
SORT_FIELDS = ['id','reads','likes','popularity']
DIRECTION_FIELDS = ['asc','desc']
class APITestCase(TestCase): 
    def test_ping_views(self):
        #test variables
        test_string = '/api/ping'
        correct_response = JsonResponse({"success":True}, status = 200)
        #test methods
        rf = Client()
        test_response = rf.get(test_string)

        #test response
        self.assertEqual(test_response.status_code, correct_response.status_code)
        self.assertEqual(
            str(test_response.content, encoding='utf8'),
            str(correct_response.content, encoding='utf8')
        )
    def test_posts_null(self):
        #test variables
        test_string = '/api/posts'
        correct_response = JsonResponse({"error": "Tags parameter is required"}, status = 400)
        #test methods
        rf = Client()
        test_response = rf.get(test_string)
        #test response
        self.assertEqual(test_response.status_code, correct_response.status_code)
        self.assertEqual(
            str(test_response.content, encoding='utf8'),
            str(correct_response.content, encoding='utf8')
        )
    def test_posts_invalid_sortBy(self):
        #test variables
        test_string = '/api/posts?tags=tech&sortBy=sdfaf'
        correct_response = JsonResponse({"error": "sortBy parameter is invalid"}, status = 400)
        #test methods
        rf = Client()
        test_response = rf.get(test_string)
        #test response
        self.assertEqual(test_response.status_code, correct_response.status_code)
        self.assertEqual(
            str(test_response.content, encoding='utf8'),
            str(correct_response.content, encoding='utf8')
        )
    def test_posts_invalid_direction(self):
        #test variables
        test_string = '/api/posts?tags=tech&sortBy=id&direction=asc,desc'
        correct_response = JsonResponse({"error": "direction parameter is invalid"}, status = 400)
        #test methods
        rf = Client()
        test_response = rf.get(test_string)
        #test response
        self.assertEqual(test_response.status_code, correct_response.status_code)
        self.assertEqual(
            str(test_response.content, encoding='utf8'),
            str(correct_response.content, encoding='utf8')
        )
    def test_posts_duplicate(self):
        #test variables
        test_string = '/api/posts?tags=tech,science,health'
        #test methods
        rf = Client()
        response = rf.get(test_string)
        test_response = json.loads(str(response.content,encoding='utf8'))['posts']
        self.assertEqual(response.status_code, 200)
        #test response
        for i in range(0,len(test_response)):
            for j in range(0,len(test_response)):
                if i != j:
                    self.assertNotEqual(test_response[i],test_response[j])
    def test_posts_tech(self):
        #test variables
        test_string = '/api/posts?tags=tech'
        #test methods
        rf = Client()
        response = rf.get(test_string)
        test_response = json.loads(str(response.content,encoding='utf8'))['posts']
        self.assertEqual(response.status_code, 200)
        #test response
        for i in test_response:
            self.assertIn('tech',i['tags'])
    def test_posts_tech_science(self):
        #test variables
        test_string = '/api/posts?tags=tech,science'
        #test methods
        rf = Client()
        response = rf.get(test_string)
        test_response = json.loads(str(response.content,encoding='utf8'))['posts']
        self.assertEqual(response.status_code, 200)
        #test response
        for i in test_response:
            self.assertTrue('tech' in i['tags'] or 'science' in i['tags'])
    def test_posts_tech_health_sortBy(self):
        #test variables
        for s in SORT_FIELDS:
            with self.subTest(s=s):
                test_string = '/api/posts?tags=tech,health&sortBy='+s
                #test methods
                rf = Client()
                response = rf.get(test_string)
                test_response = json.loads(str(response.content,encoding='utf8'))['posts']
                self.assertEqual(response.status_code, 200)
                #test response
                old = test_response[0][s]
                for i in test_response[1:]:
                    self.assertTrue(i[s] >= old)
                    old = i[s]
    def test_posts_tech_science_sortBy_direction(self):
        #test variables
        for s in SORT_FIELDS:
            for d in DIRECTION_FIELDS:
                with self.subTest(s=s,d=d):
                    test_string = '/api/posts?tags=tech,science&sortBy='+s+'&direction='+d
                    #test methods
                    rf = Client()
                    response = rf.get(test_string)
                    test_response = json.loads(str(response.content,encoding='utf8'))['posts']
                    self.assertEqual(response.status_code, 200)
                    #test response
                    old = test_response[0]
                    self.assertTrue('tech' in old['tags'] or 'science' in old['tags'])
                    for i in test_response[1:]:
                        if d == 'asc':
                            self.assertTrue(i[s] >= old[s])
                        else:
                            self.assertTrue(i[s] <= old[s])
                        old = i
                        self.assertTrue('tech' in i['tags'] or 'science' in i['tags'])
    



