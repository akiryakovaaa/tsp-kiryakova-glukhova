import sys
import os
import grpc

# добавляем пути к папкам с файлами проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos'))) # папка \protos

import service_pb2
import service_pb2_grpc


def get_similar_posts(post_id: int, tags: list[str]):
    # открываем канал для подключения к gRPC-серверу
    with grpc.insecure_channel("localhost:50051") as channel:
        # создаем клиент для вызова метода gRPC-сервиса
        stub = service_pb2_grpc.SimilarityServiceStub(channel)

        # формируем запрос с id публикации и ее тегами
        request = service_pb2.PostRequest(
            post_id=post_id,
            tags=tags
        )

        try:
            # отправляем запрос и получаем ответ от gRPC-сервера
            response = stub.GetSimilarPosts(request, timeout=5.0)

            # преобразуем ответ в список словарей для FastAPI
            return [{"id": post.id, "title": post.title} for post in response.posts]

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                print(f"[gRPC] Ошибка: Сервер не ответил за 5 секунд.")
            else:
                print(f"[gRPC] Внутренняя ошибка сети: {e.details()}")

            return []