import pickle

def load_model():
    with open("/opt/models/best_model.pkl", "rb") as f:
        model = pickle.load(f)
    return model