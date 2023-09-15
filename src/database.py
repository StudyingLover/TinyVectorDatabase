import numpy as np
from collections import defaultdict
from typing import List, Tuple
import pickle
from PIL import Image

from src.encoder import image_to_features, text_to_features

# 计算余弦相似度
def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

# 向量数据库的类
class VectorDatabase:
    def __init__(self):
        self.vectors = defaultdict(np.ndarray) # 用于存储向量的字典
        self.vector_dim = 768 # 向量维度

    def insert(self, key: str, vector: np.ndarray) -> None:
        if self.vector_dim is None:
            self.vector_dim = vector.shape[0]
        else:
            if vector.shape[0] != self.vector_dim:
                raise ValueError("Vector dimension mismatch", vector.shape[0], self.vector_dim)
            
        # 判断key是否已经存在
        if key in self.vectors:
            raise ValueError("Key already exists")
        self.vectors[key] = vector
    
    def delete(self, key: str) -> None:
        del self.vectors[key]   

    def search(self, query_vector: np.ndarray, k: int) -> List[Tuple[str, float]]:
        if query_vector.shape[0] != self.vector_dim:
            raise ValueError("Query vector dimension mismatch")
        similarities = [(key, cosine_similarity(query_vector, vector)) for key, vector in self.vectors.items()]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def retrieve(self, key: str) -> np.ndarray:
        return self.vectors.get(key, None)

    def save_database(self, file_path: str) -> None:
        with open(file_path, 'wb') as file:
            pickle.dump(self.vectors, file)

    def get_all_keys(self) -> List[str]:
        return list(self.vectors.keys())
    
    @classmethod
    def load_database(cls, file_path: str) -> 'VectorDatabase':
        with open(file_path, 'rb') as file:
            vectors = pickle.load(file)
        database = cls()
        database.vectors = vectors
        return database

if __name__ == '__main__':
    # # 创建一个VectorDatabase对象
    # database = VectorDatabase()

    # # 插入向量
    # database.insert('key1', np.array([1, 2, 3]))
    # database.insert('key2', np.array([4, 5, 6]))

    # # 保存数据库到文件
    # database.save_database('vector_db.pkl')

    # # 从文件中加载数据库
    # loaded_db = VectorDatabase.load_database('vector_db.pkl')
    
    # quary = np.array([4, 4, 3])
    # # 检索
    # result = loaded_db.search(quary, 1)
    # print(result)  # 输出: [('key1', 1.0)]
    
    # vector_insert = np.array([7, 2, 3])
    # # 插入
    # loaded_db.insert('key3', vector_insert)
    
    # quary2 = np.array([7, 2, 3])
    # # 检索
    # result = loaded_db.search(quary2, 2)
    # print(result)  # 输出: [('key3', 1.0), ('key1', 0.9258200997725515)]
    
    # # 保存到文件
    # loaded_db.save_database('vector_db.pkl')

    # # 检索向量
    # vector = loaded_db.retrieve('key1')
    # print(vector)  # 输出: [1 2 3]
    
    img = Image.open("example.png")
    img_vector = image_to_features(img)
    database = VectorDatabase()
    database.insert('example_img', img_vector)
    text = "a photo of mountain and water"
    text_vector = text_to_features(text)
    # database.insert('example_text', text_vector)
    
    # 随机生成10个向量插入
    for i in range(10):
        database.insert(str(i), np.random.rand(768))
    database.save_database('vector_db.pkl')
    database.delete('example_img')
    result = database.search(text_vector, 1)
    
    print(result)
    