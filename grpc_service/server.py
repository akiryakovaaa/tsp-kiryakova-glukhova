import sys
import os
import grpc
from concurrent import futures

# добавляем пути к папкам с файлами проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../protos'))) # папка \protos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # папка \tsp-kiryakova-glukhova

import service_pb2
import service_pb2_grpc
from database import SessionLocal
import crud

# класс обрабатывает запросы от gRPC-клиента
class SimilarityServiceServicer(service_pb2_grpc.SimilarityServiceServicer):
    def GetSimilarPosts(self, request, context):
        # выводим данные запроса в консоль для проверки работы сервиса
        print(
            f"[gRPC] Поиск похожих постов: "
            f"ID={request.post_id}, теги={list(request.tags)}"
        )

        # создаем объект для ответа клиенту
        response = service_pb2.PostListResponse()

        db = SessionLocal()

        try:
            post = crud.get_post_by_id(db, request.post_id)

            if post is None:
                return response

            # сохраняем теги публикации в множество в нижнем регистре
            tag_names = {tag.name.lower() for tag in post.tags}

            if not tag_names:
                return response

            all_posts = crud.get_all_posts(db)
            similar_posts = []

            for candidate in all_posts:
                # исключаем исходную публикацию из результатов
                if candidate.id == post.id:
                    continue

                # получаем теги текущей публикации в множестве
                candidate_tags = {tag.name.lower() for tag in candidate.tags}

                # находим общие теги двух публикаций
                common_tags = tag_names & candidate_tags

                # добавляем публикацию, если найден хотя бы один общий тег
                if common_tags:
                    similar_posts.append((candidate, len(common_tags)))

            # сначала показываем публикации с большим числом общих тегов
            # при равном количестве общих тегов раньше идет публикация с меньшим id
            similar_posts.sort(key=lambda item: (-item[1], item[0].id))

            # добавляем в ответ не более пяти похожих публикаций
            for candidate, _ in similar_posts[:5]:
                response.posts.add(
                    id=candidate.id,
                    title=candidate.title
                )

            return response

        except Exception as exc:
            print(f"[gRPC] Ошибка поиска: {exc}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return response

        finally:
            db.close()


def serve():
    # создаем gRPC-сервер с пулом из десяти рабочих потоков
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # регистрируем обработчик запросов на сервере
    service_pb2_grpc.add_SimilarityServiceServicer_to_server(
        SimilarityServiceServicer(), server
    )

    server.add_insecure_port('[::]:50051')
    print("gRPC сервер запущен на порту 50051...")

    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
