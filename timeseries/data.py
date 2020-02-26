# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/80_timeseries_data.ipynb (unless otherwise specified).

__all__ = ['TSData', 'get_ts_items', 'show_timeseries', 'file_extract_at_filename', 'unzip_data', 'URLs_TS',
           'get_UCR_univariate_list', 'get_UCR_multivariate_list']

# Cell
from fastai2.basics import *
# from fastai2.data.all import *

# Cell
from zipfile import ZipFile

# Cell
@docs
class TSData():
    "Class that loads .arff (soon .ts) files and returns a tuple (data.x , self.y)"
    "self.x is a list of 2D array with a shape (n_samples, nb_channels, sequence_length) "
    "self.y is a 1D array as y (i.e. label) with a shape (n_samples)"
    "for the NATOPS_Train.arff file, the result will be : x(180, 24, 51) and y(180)"
    # def __init__(self):
    #     self.x = self.y = self.dsname = self.fnames = [],[],[],[]

    def __init__(self, fnames, has_targets=True, fill_missing='NaN'):
        # self.x = self.y = self.dsname = [],[],[]
        self.x = []
        self.y = []
        self.dsname = []
        self.fnames = fnames
        self.has_targets = has_targets
        self.fill_missings = fill_missing

    def __repr__(self): return f"{self.__class__.__name__}:\n Datasets names (concatenated): {self.dsname}\n Filenames:                     {self.fnames}\n Data shape: {self.x.shape}\n Targets shape: {self.y.shape}\n Nb Samples: {self.x.shape[0]}\n Nb Channels:           {self.x.shape[1]}\n Sequence Length: {self.x.shape[2]}"

    def get_x(self, as_list=True): return(list(self.x))
    def get_y(self): return(self.y)
    def get_items(self): return [(item, str(label)) for (item, label) in zip(list(self.x), self.y)]
    def __getitem__(self, i): return (self.x[i], str(self.y[i]))

    @property
    def sizes(self): return (self.x.shape, self.y.shape)

    @property
    def n_channels(self): return (self.x.shape[1])

    def _load_arff(self, fname, has_targets=True, fill_missing='NaN'):
        "load an .arff file and return a tupple of 2 numpy arrays: "
        "x : array with a shape (n_samples, nb_channels, sequence_length)"
        "y : array with a shape (n_samples)"
        "for the NATOPS_Train.arff  the result will be : x(180, 24, 51) and y(180)"

        instance_list = []
        class_val_list = []
        data_started = False
        is_multi_variate = False
        is_first_case = True

        with open(fname, 'r') as f:
            for line in f:
                if line.strip():
                    if is_multi_variate is False and "@attribute" in line.lower() and "relational" in line.lower():
                        is_multi_variate = True
                    if "@data" in line.lower():
                        data_started = True
                        continue
                    # if the 'data tag has been found, the header information has been cleared and now data can be loaded
                    if data_started:
                        line = line.replace("?", fill_missing)
                        if is_multi_variate:
                            if has_targets:
                                line, class_val = line.split("',")
                                class_val_list.append(class_val.strip())
                            dimensions = line.split("\\n")
                            dimensions[0] = dimensions[0].replace("'", "")

                            if is_first_case:
                                for d in range(len(dimensions)):
                                    instance_list.append([])
                                is_first_case = False

                            for dim in range(len(dimensions)):
                                instance_list[dim].append(np.array(dimensions[dim].split(','), dtype=np.float32))
#                                 instance_list[dim].append(np.fromiter(dimensions[dim].split(','), dtype=np.float32))
                        else:
                            if is_first_case:
                                instance_list.append([])
                                is_first_case = False

                            line_parts = line.split(",")

                            if has_targets:
                                instance_list[0].append(np.array(line_parts[:len(line_parts)-1], dtype=np.float32))

                                class_val_list.append(line_parts[-1].strip())
                            else:
                                instance_list[0].append(np.array(line_parts[:len(line_parts)-1], dtype=np.float32))

        #instance_list has a shape of (dimensions, nb_samples, seq_lenght)
        #for the NATOPS_Train.arff it would be (24, 180, 51)
        #convert python list to numpy array and transpose the 2 first dimensions -> (180, 24, 51)
        x = np.asarray(instance_list).transpose(1,0,2)

        if has_targets:
            y = np.asarray(class_val_list)
            return x, y
        else:
            return x, [None*x.shape[0]]

    @classmethod
    def from_arff(self, fnames, has_targets=True, fill_missing='NaN'):
        "load an .arff file and return a tupple of 2 numpy arrays: "
        "x : array with a shape (n_samples, nb_channels, sequence_length)"
        "y : array with a shape (n_samples)"
        "for the NATOPS_Train.arff  the result will be : x(180, 24, 51) and y(180)"
        data = self(fnames, has_targets=has_targets, fill_missing=fill_missing)
        if isinstance(fnames, list):
            data.x = []
            data.y = []
            data.dsname = []
            data.fnames = []
            xs,ys = [],[]
            for i, fn in enumerate(fnames):
                x,y = data._load_arff(fn, has_targets=has_targets, fill_missing=fill_missing)
                xs.append(x)
                ys.append(y)
                data.fnames.append(fn)
                data.dsname.append(fn.stem)
            data.x = np.concatenate(xs)
            data.y = np.concatenate(ys)
        else:
            data.fnames.append(fnames)
            data.dsname.append(fnames.stem)
            data.x, data.y = data._load(fnames, has_targets=has_targets, fill_missing=fill_missing)

        return data

# add_docs(TSData,
#          from_arff="read one or serveral arff files and concatenate them, and returns a TSData object")

    _docs=dict(
         from_arff="read one or serveral arff files and concatenate them, and returns a TSData object",
         get_items="return list of tuples. Each tuple corresponds to a timeserie (nump.ndarray) and a label (string)",
         get_x="return list of timeseries (no labels)",
         get_y="return list of labels corresponding to each timeserie",
         sizes="return timeseries shape and labels shape (labels list size)",
         n_channels="return timeserie's number of channels. For `arff` files it is called `dimension`. In the case of NATOPS_Train.arff, it returns 24")

# Cell
def get_ts_items(fnames):
    'get_ts_items return list of tuples. Each tuple corresponds to a timeserie (nump.ndarray) and a label (string)'
    data = TSData.from_arff(fnames)
    return data.get_items()

# Cell
def show_timeseries(ts, ctx=None, title=None, chs=None, leg=True, **kwargs):
    """
    Plot a timeseries.

    Args:

        title : usually the class of the timeseries

        ts : timeseries. It should have a shape of (nb_channels, sequence_length)

        chs : array representing a list of channels to plot

        leg : Display or not a legend
    """

    if ctx is None: fig, ctx = plt.subplots()
    t = range(ts.shape[1])
    chs_max = max(chs) if chs else 0
    channels = chs if (chs and (chs_max < ts.shape[0])) else range(ts.shape[0])
    for ch in channels:
        ctx.plot(t, ts[ch], label='ch'+str(ch))
    if leg: ctx.legend(loc='upper right', ncol=2, framealpha=0.5)
    if title: ctx.set_title(title)
    return ctx

# Cell
def file_extract_at_filename(fname, dest):
    "Extract `fname` to `dest`/`fname`.name folder using `tarfile` or `zipfile"
    dest = Path(dest)/Path(fname).with_suffix('').name
    # tarfile.open(fname, 'r:gz').extractall(dest)
    fname = str(fname)
    if   fname.endswith('gz'):  tarfile.open(fname, 'r:gz').extractall(dest)
    elif fname.endswith('zip'): zipfile.ZipFile(fname     ).extractall(dest)
    else: raise Exception(f'Unrecognized archive: {fname}')

# Cell
def unzip_data(url, fname=None, dest=None, c_key='data', force_download=False):
    "Download `url` to `fname` if `dest` doesn't exist, and un-compress to `dest`/`fname`.name folder ."
    return untar_data(url, fname=fname, c_key=c_key, force_download=force_download, extract_func=file_extract_at_filename)


# Cell
class URLs_TS():
    "Global constants for dataset and model URLs."
    LOCAL_PATH = Path.cwd()
    URL = 'http://www.timeseriesclassification.com/Downloads/'


    # UCRmultivariate datasets
    ARTICULARY_WORD_RECOGNITION   = f'{URL}ArticularyWordRecognition.zip'
    ATRIAL_FIBRILLATION           = f'{URL}AtrialFibrillation.zip'
    BASIC_MOTIONS                 = f'{URL}BasicMotions.zip'
    CHARACTER_TRAJECTORIES        = f'{URL}CharacterTrajectories.zip'
    CRICKET                       = f'{URL}Cricket.zip'
    DUCK_DUCK_GEESE               = f'{URL}DuckDuckGeese.zip'
    EIGEN_WORMS                   = f'{URL}EigenWorms.zip'
    EPILEPSY                      = f'{URL}Epilepsy.zip'
    ETHANOL_CONCENTRATION         = f'{URL}EthanolConcentration.zip'
    ERING                        = f'{URL}ERing.zip'
    FACE_DETECTION                = f'{URL}FaceDetection.zip'
    FINGER_MOVEMENTS              = f'{URL}FingerMovements.zip'
    HAND_MOVEMENT_DIRECTION       = f'{URL}HandMovementDirection.zip'
    HANDWRITING                   = f'{URL}Handwriting.zip'
    HEARTBEAT                     = f'{URL}Heartbeat.zip'
    JAPANESE_VOWELS               = f'{URL}JapaneseVowels.zip'
    LIBRAS                        = f'{URL}Libras.zip'
    LSST                          = f'{URL}LSST.zip'
    INSECT_WINGBEAT               = f'{URL}InsectWingbeat.zip'
    MOTOR_IMAGERY                 = f'{URL}MotorImagery.zip'
    NATOPS                        = f'{URL}NATOPS.zip'
    PEN_DIGITS                    = f'{URL}PenDigits.zip'
    PEMS_SF                       = f'{URL}PEMS-SF.zip'
    PHONEME_SPECTRA               = f'{URL}PhonemeSpectra.zip'
    RACKET_SPORTS                 = f'{URL}RacketSports.zip'
    SELF_REGULATION_SCP1          = f'{URL}SelfRegulationSCP1.zip'
    SELF_REGULATION_SCP2          = f'{URL}SelfRegulationSCP2.zip'
    SPOKEN_ARABIC_DIGITS          = f'{URL}SpokenArabicDigits.zip'
    STAND_WALK_JUMP               = f'{URL}StandWalkJump.zip'
    UWAVE_GESTURE_LIBRARY        = f'{URL}UWaveGestureLibrary.zip'

    def path(url='.', c_key='archive'):
        fname = url.split('/')[-1]
        local_path = URLs.LOCAL_PATH/('models' if c_key=='models' else 'data')/fname
        if local_path.exists(): return local_path
        return Config()[c_key]/fname

# Cell
def get_UCR_univariate_list():
    return [
        'ACSF1', 'Adiac', 'AllGestureWiimoteX', 'AllGestureWiimoteY',
        'AllGestureWiimoteZ', 'ArrowHead', 'Beef', 'BeetleFly', 'BirdChicken',
        'BME', 'Car', 'CBF', 'Chinatown', 'ChlorineConcentration',
        'CinCECGtorso', 'Coffee', 'Computers', 'CricketX', 'CricketY',
        'CricketZ', 'Crop', 'DiatomSizeReduction',
        'DistalPhalanxOutlineAgeGroup', 'DistalPhalanxOutlineCorrect',
        'DistalPhalanxTW', 'DodgerLoopDay', 'DodgerLoopGame',
        'DodgerLoopWeekend', 'Earthquakes', 'ECG200', 'ECG5000', 'ECGFiveDays',
        'ElectricDevices', 'EOGHorizontalSignal', 'EOGVerticalSignal',
        'EthanolLevel', 'FaceAll', 'FaceFour', 'FacesUCR', 'FiftyWords',
        'Fish', 'FordA', 'FordB', 'FreezerRegularTrain', 'FreezerSmallTrain',
        'Fungi', 'GestureMidAirD1', 'GestureMidAirD2', 'GestureMidAirD3',
        'GesturePebbleZ1', 'GesturePebbleZ2', 'GunPoint', 'GunPointAgeSpan',
        'GunPointMaleVersusFemale', 'GunPointOldVersusYoung', 'Ham',
        'HandOutlines', 'Haptics', 'Herring', 'HouseTwenty', 'InlineSkate',
        'InsectEPGRegularTrain', 'InsectEPGSmallTrain', 'InsectWingbeatSound',
        'ItalyPowerDemand', 'LargeKitchenAppliances', 'Lightning2',
        'Lightning7', 'Mallat', 'Meat', 'MedicalImages', 'MelbournePedestrian',
        'MiddlePhalanxOutlineAgeGroup', 'MiddlePhalanxOutlineCorrect',
        'MiddlePhalanxTW', 'MixedShapes', 'MixedShapesSmallTrain',
        'MoteStrain', 'NonInvasiveFetalECGThorax1',
        'NonInvasiveFetalECGThorax2', 'OliveOil', 'OSULeaf',
        'PhalangesOutlinesCorrect', 'Phoneme', 'PickupGestureWiimoteZ',
        'PigAirwayPressure', 'PigArtPressure', 'PigCVP', 'PLAID', 'Plane',
        'PowerCons', 'ProximalPhalanxOutlineAgeGroup',
        'ProximalPhalanxOutlineCorrect', 'ProximalPhalanxTW',
        'RefrigerationDevices', 'Rock', 'ScreenType', 'SemgHandGenderCh2',
        'SemgHandMovementCh2', 'SemgHandSubjectCh2', 'ShakeGestureWiimoteZ',
        'ShapeletSim', 'ShapesAll', 'SmallKitchenAppliances', 'SmoothSubspace',
        'SonyAIBORobotSurface1', 'SonyAIBORobotSurface2', 'StarlightCurves',
        'Strawberry', 'SwedishLeaf', 'Symbols', 'SyntheticControl',
        'ToeSegmentation1', 'ToeSegmentation2', 'Trace', 'TwoLeadECG',
        'TwoPatterns', 'UMD', 'UWaveGestureLibraryAll', 'UWaveGestureLibraryX',
        'UWaveGestureLibraryY', 'UWaveGestureLibraryZ', 'Wafer', 'Wine',
        'WordSynonyms', 'Worms', 'WormsTwoClass', 'Yoga'
    ]

def get_UCR_multivariate_list():
    return [
        'ArticularyWordRecognition', 'AtrialFibrillation', 'BasicMotions',
        'CharacterTrajectories', 'Cricket', 'DuckDuckGeese', 'EigenWorms',
        'Epilepsy', 'EthanolConcentration', 'ERing', 'FaceDetection',
        'FingerMovements', 'HandMovementDirection', 'Handwriting', 'Heartbeat',
        'JapaneseVowels', 'Libras', 'LSST', 'InsectWingbeat', 'MotorImagery',
        'NATOPS', 'PenDigits', 'PEMS-SF', 'PhonemeSpectra', 'RacketSports',
        'SelfRegulationSCP1', 'SelfRegulationSCP2', 'SpokenArabicDigits',
        'StandWalkJump', 'UWaveGestureLibrary'
    ]