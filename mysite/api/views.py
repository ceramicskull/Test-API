from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import json
from threading import Thread
from queue import Queue
SORT_FIELDS = ['id','reads','likes','popularity',None]
DIRECTION_FIELDS = ['asc','desc',None]
def index(request):
    return HttpResponse("Please use api")

def ping(request):
    print(request)
    return JsonResponse({"success":True}, status = 200)

def posts(request):
    if request.method == 'GET':
        gets = request.GET
        try:
            tags = gets['tags']
        except:
            return JsonResponse({"error":"Tags parameter is required"}, status = 400)    
        try:
            sortBy = gets['sortBy']
        except:
            sortBy = None
        try:
            direction = gets['direction']
        except:
            direction = None
        if sortBy not in SORT_FIELDS:
            return JsonResponse({"error":"sortBy parameter is invalid"}, status = 400)
        if direction not in DIRECTION_FIELDS:
            return JsonResponse({"error":"direction parameter is invalid"}, status = 400)
        
        tags=tags.split(',')
        #concurrently get api requests
        queue = Queue()
        rqueue = Queue()
        # Create 8 worker threads
        if len(tags) > 8: 
            num_workers = 8
        else:
            num_workers = len(tags)
        for x in range(num_workers):
            worker = RequestWorker(queue,rqueue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()
        # Put the tasks into the queue as a tuple
        for tag in tags:
            queue.put(tag)
        # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()
        posts = []
        while not rqueue.empty():
              posts += rqueue.get().json()['posts']
        posts = [json.loads(s) for s in set(json.dumps(d) for d in posts)]
        print(posts)
        if sortBy == None:
            response = { 'posts': posts }
        elif direction == 'desc':
            response = { 'posts': sorted(posts,key=lambda i: i[sortBy], reverse=True), }
        else:
            response = { 'posts': sorted(posts,key=lambda i: i[sortBy]), }
        return JsonResponse(response, status = 200)
    else:
        return JsonResponse({"error":"Not a GET request"}, status = 400)


class RequestWorker(Thread):

    def __init__(self, queue,rqueue):
        Thread.__init__(self)
        self.queue = queue
        self.rqueue = rqueue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            tag = self.queue.get()
            try:
                response = requests.get('https://api.hatchways.io/assessment/blog/posts?tag=' + tag)
                self.rqueue.put(response)
            finally:
                self.queue.task_done()