import pytest

from fe.access.new_searcher import register_new_searcher
from fe.test.add_store_book import AddStoreBook
import uuid
import random

class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.searcher_id = "test_search_searcher_id_{}".format(str(uuid.uuid1()))
        self.password = self.searcher_id
        self.searcher = register_new_searcher(self.searcher_id, self.password)

        self.store_id1 = "test_search_store_id_{}".format(str(uuid.uuid1())) #店铺内
        #self.store_id1 = 'test_search_store_id_4886fd75-761c-11ed-8bc4-145afc1fa211'
        self.store_id0 = "" #全站
        self.add1 = AddStoreBook(self.store_id1) #店铺内
        self.add0 = AddStoreBook(self.store_id0) #全站

        self.keyword1 = "美丽人生"
        self.keyword0 = "繺"
        self.page = 0

        yield

    def test_store_ok(self):

        ok = self.add1.add()
        assert ok

        code1,pagenum,row,_ = self.searcher.search(self.store_id1, self.keyword1, True)
        assert code1 == 200

        if pagenum > 1:
            self.page = random.randint(1,pagenum)
            code2,_,_,_ = self.searcher.show_pages(self.page, row, True)
            assert code2 == 200

    def test_all_ok(self):

        ok = self.add0.add()
        assert ok

        code1, pagenum, row, _ = self.searcher.search(self.store_id0, self.keyword1, True)
        assert code1 == 200

        if pagenum > 1:
            self.page = random.randint(1, pagenum)
            code2, _, _, _ = self.searcher.show_pages(self.page, row, True)
            assert code2 == 200

    def test_error_non_exist_search(self):

        ok = self.add0.add()
        assert ok

        code = self.searcher.search(self.store_id1, self.keyword0, False)
        assert code != 200

    def test_non_exist_user_id(self):

        ok = self.add0.add()
        assert ok

        self.searcher.user_id = self.searcher.user_id + "_x"
        code = self.searcher.search(self.store_id1, self.keyword1, False)
        assert code != 200

    def test_non_exist_store_id(self):

        ok = self.add0.add()
        assert ok

        code = self.searcher.search(self.store_id1+"x", self.keyword1 ,False)
        assert code != 200