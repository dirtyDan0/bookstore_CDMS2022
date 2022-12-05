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
        self.store_id0 = None #全站
        self.add1 = AddStoreBook(self.store_id1) #店铺内
        self.add0 = AddStoreBook(self.store_id0) #全站

        self.keyword = '人'
        self.page = 0

        yield

    def test_store_ok(self):
        ok = self.add1
        assert ok
        #code1,pagenum,row,_ = self.searcher.search(self.store_id1, self.keyword)
        code1 = self.searcher.search(store_id=self.store_id1, keyword=self.keyword)
        assert code1 == 200
        """
        if pagenum != 0:
            self.page = random.randint(0,pagenum)
            code2,_,_,_ = self.searcher.show_pages(self.page, row)
            assert code2 == 200
        """
    def test_all_ok(self):
        ok = self.add0
        assert ok
        code1, pagenum, row, _ = self.searcher.search(self.store_id0, self.keyword)
        assert code1 == 200
        if pagenum != 0:
            self.page = random.randint(0, pagenum)
            code2, _, _, _ = self.searcher.show_pages(self.page, row)
            assert code2 == 200

    def test_error_non_exist_search(self):
        ok = self.add0
        assert ok
        code,_,_,_ = self.searcher.search(self.store_id1, self.keyword+"xx")
        assert code == 200

    def test_non_exist_user_id(self):
        ok = self.add0
        assert ok
        self.searcher.user_id = self.searcher.user_id + "_x"
        code, _, _, _ = self.searcher.search(self.store_id1, self.keyword)
        assert code == 200

    def test_non_exist_store_id(self):
        ok = self.add0
        assert ok
        code,_,_,_ = self.searcher.search(self.store_id1+"x", self.keyword)
        assert code != 200