import grpc

from protos import service_pb2, service_pb2_grpc


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

        # отправляем запрос и получаем ответ от gRPC-сервера
        response = stub.GetSimilarPosts(request)

        # преобразуем ответ в список словарей для FastAPI
        return [
            {
                "id": post.id,
                "title": post.title
            }
            for post in response.posts
        ]
