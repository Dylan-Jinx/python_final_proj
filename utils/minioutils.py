import base64
import io

from minio import Minio


class MinioStore:

    def __init__(self,
                 host='42.192.5.34:9000',
                 access_key='minioadmin',
                 secret_key='cSLxZqgpn2$DcHxb4Kx&SD@msZZOPG6s7UpF@hPYcMywsyLW5nhw9QZabsSlz0gb',
                 bucket="pythonfinalproject",
                 model_dirs='/'):
        self.host = host
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = False
        self.bucket = bucket
        self.model_dirs = model_dirs
        self.client = Minio(
            self.host,
            secure=self.secure,
            access_key=self.access_key,
            secret_key=self.secret_key,
        )

        def __new__(cls, *args, **kw) -> object:
            """
            启用单例模式
            :param args:
            :param kw:
            :return:
            """
            if not hasattr(cls, '_instance'):
                cls._instance = object.__new__(cls)
            return cls._instance

    def get_origin_object(self, file_name) -> object:

        found = self.client.bucket_exists(self.bucket)
        if not found:
            self.client.make_bucket(self.bucket)
            print(f'create {self.bucket} success')

        model_file = self.model_dirs + file_name
        data = self.client.get_object(
            self.bucket, file_name)
        return data

    def get_object(self, file_name) -> object:

        found = self.client.bucket_exists(self.bucket)
        if not found:
            self.client.make_bucket(self.bucket)
            print(f'create {self.bucket} success')

        model_file = self.model_dirs + file_name
        data = self.client.get_object(
            self.bucket, file_name)

        with open(model_file, 'wb') as f:
            for d in data:
                f.write(d)
        return model_file

    def put_object(self, object_name, raw_data, raw_size) -> object:

        found = self.client.bucket_exists(self.bucket)
        if not found:
            self.client.make_bucket(self.bucket)
            print(f'create {self.bucket} sucess！')

        return self.client.put_object(
            self.bucket, object_name, raw_data, raw_size
        )

    def fget_object(self, object_name, file_name) -> object:
        self.client.fget_object(
            self.bucket, object_name, file_name)

    def fput_object(self, object_name, file_name) -> object:
        self.client.fput_object(
            self.bucket, object_name, file_name)


if __name__ == '__main__':
    miniostore_ = MinioStore(model_dirs="/")
    data = miniostore_.get_origin_object('user_icon/admin_login.png')
    bytes_stream = io.BytesIO(data.data)
    res_data = "data:image/jpeg;base64," + base64.b64encode(data.data).decode()
    print(res_data)