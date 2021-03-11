from enum import Enum  #utilizar enums p pegar o ambiente onde vai fazer o doploy
from aws_cdk import core
from aws_cdk import (
    aws_s3 as s3,
)



from data_platform.environment import Environment #importou aqui os enums de environment


# atribuiu p um Enum p ser mais confiavel do q escrever strings toda hora
class DataLakeLayer(Enum):
    RAW = 'raw'
    PROCESSED = 'processed'
    AGGREGATED = 'aggregated'


class BaseDataLakeBucket(s3.Bucket):
    #padronizar como um bucket de datalake é criado
                # score é padrão (core do App)
                # ta adicionando o environment e uma camada.
    def __init__(self, scope: core.Construct, deploy_env: Environment, layer: DataLakeLayer, **kwargs):
        self.layer = layer
        self.deploy_env = deploy_env
                        #padronizando a criação de nome dos buckets.
        self.obj_name = f's3-belisco-turma-4-{self.deploy_env.value}-data-lake-{self.layer.value}'

        super().__init__(
            scope,
            id=self.obj_name, #refere-se ao id logico uasdo no yaml do cloudformation ex: S3BucketBelisco
            bucket_name=self.obj_name,
            block_public_access=self.default_block_public_access,
            encryption=self.default_encryption,
            versioned=True,
            **kwargs
        )

        self.set_default_lifecycle_rules()

    @property
    def default_block_public_access(self):
        return s3.BlockPublicAccess(
                ignore_public_acls=True,
                block_public_acls=True,
                block_public_policy=True,
                restrict_public_buckets=True
            )

    @property
    def default_encryption(self):
        return s3.BucketEncryption.S3_MANAGED


#regras de lifecycles pra lidar com coisas do tipo passar dados p 
# camadas diferentes p baratear o custo de armazenamendo (Glacier)

    def set_default_lifecycle_rules(self):
        """
        Sets lifecycle rule by default
        """
        self.add_lifecycle_rule(
            abort_incomplete_multipart_upload_after=core.Duration.days(7),
            enabled=True
        )

        self.add_lifecycle_rule(
            noncurrent_version_transitions=[
                s3.NoncurrentVersionTransition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=core.Duration.days(30)
                ),
                s3.NoncurrentVersionTransition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=core.Duration.days(60)
                )
            ]
        )

            #expira versão 
        self.add_lifecycle_rule(
            noncurrent_version_expiration=core.Duration.days(360)
        )
