import sys
import os
import grpc
from concurrent import futures

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import service_pb2
import service_pb2_grpc
from database import SessionLocal
import crud

class SimilarityServiceServicer(service_pb2_grpc.SimilarityServiceServicer):
    def GetSimilarPosts(self, request, context):
        print(f"[gRPC] Получен запрос на поиск похожих постов для ID: {request.post_id}")
        response = service_pb2.PostListResponse()

        db = SessionLocal()
        try:
            response.posts.add(id=request.post_id + 1, title="Похожий пост №1")
            response.posts.add(id=request.post_id + 2, title="Похожий пост №2")
        finally:
            db.close()

        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_SimilarityServiceServicer_to_server(SimilarityServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC сервер запущен на порту 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()