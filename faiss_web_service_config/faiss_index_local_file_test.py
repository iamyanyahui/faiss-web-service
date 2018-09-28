def GET_FAISS_INDEX():
    import faiss

    index_file_path = '../faiss_index_files/index'
    return faiss.read_index(index_file_path)


def GET_FAISS_ID_TO_VECTOR():
    import pickle

    ids_vectors_path = '../faiss_index_files/ids_vectors.p'
    with open(ids_vectors_path, 'rb') as f:
        ids_vectors = pickle.load(f)

    def id_to_vector(id_):
        try:
            return ids_vectors[id_]
        except:
            pass

    return id_to_vector


UPDATE_FAISS_AFTER_SECONDS = 10
