import pytest
import numpy as np
from datetime import datetime, timedelta
import redis

from rafiki.test.utils import global_setup, mock_redis
from rafiki.param_store import ParamStore, ParamsType

class TestStore():    
    
    @pytest.fixture(scope='class', autouse=True)
    def params(self):
        '''
        Initializes params for testing
        '''
        return {
            '1': { 'param': np.random.normal(size=(2, 2)) },
            '2': { 'param': np.random.normal(size=(2, 2)) },
            '3': { 'param': np.random.normal(size=(2, 2)) },
            '4': { 'param': np.random.normal(size=(2, 2)) },
            '5': { 'param': np.random.normal(size=(2, 2)) },
            '6': { 'param': np.random.normal(size=(2, 2)) },
        }

    @pytest.fixture(scope='class', autouse=True)
    def stores(self):
        '''
        Initializes params stores for testing
        '''
        return {
            '1': ParamStore(worker_id='1', redis_host=True),
            '2': ParamStore(worker_id='2', redis_host=True),
            '3': ParamStore(worker_id='3', redis_host=True)
        }

    def test_get_local_recent(self, params, stores):
        # Populate params
        stores['3'].store_params(params['1'], 0.7, time=(datetime.now() - timedelta(hours=1))) # 1h ago (another worker)
        stores['1'].store_params(params['2'], 0.2, time=datetime.now()) # now
        stores['1'].store_params(params['3'], 1, time=(datetime.now() - timedelta(minutes=2))) # 2 min ago
        stores['2'].store_params(params['4'], 0.1, time=datetime.now()) # now (another worker)
        stores['1'].store_params(params['5'], 0.1, time=(datetime.now() - timedelta(minutes=1))) # 1 min ago    
        
        assert are_params_equal(stores['1'].retrieve_params(ParamsType.LOCAL_RECENT), params['2']) # Should be most recent in worker 1

        stores['1'].store_params(params['6'], 0.3, time=datetime.now()) # now

        assert are_params_equal(stores['1'].retrieve_params(ParamsType.LOCAL_RECENT), params['6']) # Should be most recent in worker 1

    def test_get_global_recent(self, params, stores):
        # Populate params
        stores['3'].store_params(params['1'], 0.7, time=(datetime.now() - timedelta(hours=1))) # 1h ago (another worker)
        stores['1'].store_params(params['2'], 0.2, time=datetime.now()) # now
        stores['1'].store_params(params['3'], 1, time=(datetime.now() - timedelta(minutes=2))) # 2 min ago
        stores['2'].store_params(params['4'], 0.1, time=datetime.now()) # now (another worker)
        stores['1'].store_params(params['5'], 0.1, time=(datetime.now() - timedelta(minutes=1))) # 1 min ago

        assert are_params_equal(stores['3'].retrieve_params(ParamsType.GLOBAL_RECENT), params['4']) # Should be most recent across all workers

    def test_get_local_best(self, params, stores):
        # Populate params
        stores['3'].store_params(params['1'], 0.7, time=(datetime.now() - timedelta(hours=1))) # 1h ago (another worker)
        stores['1'].store_params(params['2'], 0.2, time=datetime.now()) # now
        stores['1'].store_params(params['3'], 1, time=(datetime.now() - timedelta(minutes=2))) # 2 min ago
        stores['2'].store_params(params['4'], 0.1, time=datetime.now()) # now (another worker)
        stores['1'].store_params(params['5'], 0.1, time=(datetime.now() - timedelta(minutes=1))) # 1 min ago

        assert are_params_equal(stores['1'].retrieve_params(ParamsType.LOCAL_BEST), params['3']) # Should be best in worker 1

    def test_get_global_best(self, params, stores):
        # Populate params
        stores['3'].store_params(params['1'], 0.7, time=(datetime.now() - timedelta(hours=1))) # 1h ago (another worker)
        stores['1'].store_params(params['2'], 0.2, time=datetime.now()) # now
        stores['1'].store_params(params['3'], 1, time=(datetime.now() - timedelta(minutes=2))) # 2 min ago
        stores['2'].store_params(params['4'], 0.1, time=datetime.now()) # now (another worker)
        stores['1'].store_params(params['5'], 0.1, time=(datetime.now() - timedelta(minutes=1))) # 1 min ago

        assert are_params_equal(stores['2'].retrieve_params(ParamsType.GLOBAL_BEST), params['3']) # Should be best across all workers

def are_params_equal(params_1, params_2):
    if len(params_1) != len(params_2):
        return False
    
    for (k, v) in params_1.items():
        if isinstance(v, np.ndarray):
            if not np.array_equal(v, params_2[k]):
                return False
        else:
            if v != params_2[k]:
                return False

    return True 
        
             

        