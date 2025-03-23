class TaskRepositoryException(Exception):
    '''Task Query Service Exception'''
    def __init__(self, message='Task Query Service Exception'):
        '''コンストラクタ'''
        super().__init__(message)
    