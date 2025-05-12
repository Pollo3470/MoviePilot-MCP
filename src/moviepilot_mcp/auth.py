import os
import logging
import secrets
import string


class ApiKeyAuth:
    """
    API密钥认证类
    用于管理和验证API密钥
    """

    def __init__(self, env_var_name="MOVIEPILOT_API_KEY", key_length=32):
        """
        初始化API密钥认证类
        
        Aras:
            env_var_name: 存储API密钥的环境变量名称
            key_length: API密钥的长度
        """
        self.logger = logging.getLogger(__name__)
        self.env_var_name = env_var_name
        self.key_length = key_length
        self.api_key = self._get_or_create_api_key()

    def _generate_api_key(self):
        """
        生成一个随机的API密钥
        
        Returns:
            str: 生成的API密钥
        """
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(self.key_length))
        return api_key

    def _get_or_create_api_key(self):
        """
        从环境变量获取API密钥，如果不存在则创建新的
        
        Returns:
            str: API密钥
        """
        api_key = os.environ.get(self.env_var_name)

        if not api_key:
            api_key = self._generate_api_key()
            os.environ[self.env_var_name] = api_key
            self.logger.info(f"API密钥不存在，已自动生成新的API密钥: {api_key}")
            self.logger.info(f"请将此API密钥保存到环境变量 {self.env_var_name} 中")
        else:
            self.logger.debug("使用环境变量中的API密钥")

        return api_key

    def get_api_key(self):
        """
        获取当前的API密钥
        
        Returns:
            str: API密钥
        """
        return self.api_key

    def verify_api_key(self, provided_key):
        """
        验证提供的API密钥是否有效
        
        Args:
            provided_key: 待验证的API密钥
            
        Returns:
            bool: 如果API密钥有效返回True，否则返回False
        """
        if not provided_key:
            return False

        return secrets.compare_digest(provided_key, self.api_key)
