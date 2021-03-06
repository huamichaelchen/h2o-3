from ..connection import H2OConnection
from ..frame      import H2OFrame
from ..job        import H2OJob
from model_future import H2OModelFuture
from dim_reduction import H2ODimReductionModel
from autoencoder import H2OAutoEncoderModel
from multinomial import H2OMultinomialModel
from regression import H2ORegressionModel
from binomial import H2OBinomialModel
from clustering import H2OClusteringModel


def build_model(algo_params):
  if algo_params["training_frame"] is None: raise ValueError("Missing training_frame")
  x = algo_params.pop("X")
  y = algo_params.pop("y",None)
  training_frame = algo_params.pop("training_frame")
  validation_frame = algo_params.pop("validation_frame",None)
  algo  = algo_params.pop("algo")
  is_auto_encoder = algo_params is not None and "autoencoder" in algo_params and algo_params["autoencoder"] is not None
  is_unsupervised = is_auto_encoder or algo == "pca" or algo == "kmeans"
  if is_auto_encoder and y is not None: raise ValueError("y should not be specified for autoencoder.")
  if not is_unsupervised and y is None: raise ValueError("Missing response")
  return _model_build(x, y, training_frame, validation_frame, algo, algo_params)


def _model_build(x, y, tframe, vframe, algo, kwargs):
  kwargs['training_frame'] = tframe
  if vframe is not None: kwargs["validation_frame"] = vframe
  if y is not None:  kwargs['response_column'] = tframe[y].names[0]
  kwargs = dict([(k, (kwargs[k]._frame()).frame_id if isinstance(kwargs[k], H2OFrame) else kwargs[k]) for k in kwargs if kwargs[k] is not None])  # gruesome one-liner
  future_model = H2OModelFuture(H2OJob(H2OConnection.post_json("ModelBuilders/"+algo, **kwargs), job_type=(algo+" Model Build")), x)
  return _resolve_model(future_model, **kwargs)


def _resolve_model(future_model, **kwargs):
  future_model.poll()
  if '_rest_version' in kwargs.keys(): model_json = H2OConnection.get_json("Models/"+future_model.job.dest_key, _rest_version=kwargs['_rest_version'])["models"][0]
  else:                                model_json = H2OConnection.get_json("Models/"+future_model.job.dest_key)["models"][0]

  model_type = model_json["output"]["model_category"]
  if   model_type=="Binomial":     model = H2OBinomialModel(    future_model.job.dest_key,model_json)
  elif model_type=="Clustering":   model = H2OClusteringModel(  future_model.job.dest_key,model_json)
  elif model_type=="Regression":   model = H2ORegressionModel(  future_model.job.dest_key,model_json)
  elif model_type=="Multinomial":  model = H2OMultinomialModel( future_model.job.dest_key,model_json)
  elif model_type=="AutoEncoder":  model = H2OAutoEncoderModel( future_model.job.dest_key,model_json)
  elif model_type=="DimReduction": model = H2ODimReductionModel(future_model.job.dest_key,model_json)
  else: raise NotImplementedError(model_type)
  return model