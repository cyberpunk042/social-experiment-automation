from abc import ABC, abstractmethod

class SocialMediaIntegrationBase(ABC):
    @abstractmethod
    def get_posts(self, identifier):
        pass

    @abstractmethod
    def post_response(self, post_id, response):
        pass