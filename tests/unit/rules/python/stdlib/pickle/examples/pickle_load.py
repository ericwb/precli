import pickle


def load_pickle_file(file_path):
    # WARNING: Unpickle data without proper validation
    obj = pickle.load(file_path)
    return obj


# Example usage (assuming 'malicious.pickle' contains malicious code)
pickle_file = "malicious.pickle"
loaded_object = load_pickle_file(pickle_file)