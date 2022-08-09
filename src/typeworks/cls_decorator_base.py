
import dataclasses

from typeworks.impl.typeinfo import TypeInfo

class ClsDecoratorBase(object):
    
    IS_SUBCLASS_TYPES = []
    TYPE_PROCESSING_HOOKS = []

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        self.typeinfo = None
        self.T = None
        
    def pre_decorate(self, T):
        pass
    
    def pre_init_annotated_fields(self):
        pass
    
    def init_annotated_field(self, key, value, has_init):
        pass
    
    def post_init_annotated_fields(self):
        pass
    
    def set_field_initial(self, key, init):
        setattr(self.T, key, init)
        
    def add_field_decl(self, key, type, has_init, init=None):
        if type is None and not has_init:
            raise Exception("add_field_decl requires either a non-None type or an initial value")
        
        if type is not None:
            if not hasattr(self.T, "__annotations__"):
                setattr(self.T, "__annotations__", dict())
            self.T.__annotations__[key] = type
            
        if has_init:
            setattr(self.T, key, init)
    
    def decorate(self, T):
        return dataclasses.dataclass(T, **self.kwargs)
    
    def post_decorate(self, T, Tp):
        pass
    
    def get_typeinfo(self):
        if self.typeinfo is None:
            self.typeinfo = TypeInfo.get(self.T)
        return self.typeinfo
    
    def __call__(self, T):
        
        self.T = T
        
        print("IS_SUBCLASS_TYPES=%s" % str(type(self).IS_SUBCLASS_TYPES))

        ti = self.get_typeinfo()
        
        if hasattr(T, "__post_init__"):
            ti._post_init = T.__post_init__
        
        self.pre_decorate(T)

        self.pre_init_annotated_fields()        
        for key,value in getattr(T, "__annotations__", {}).items():
            self.init_annotated_field(key, value, hasattr(T, key))
        self.post_init_annotated_fields()
                    
        Tp = self.decorate(T)
        
        ti.Tp = Tp
        ti._decorator_init = Tp.__init__
        
        self.post_decorate(T, Tp)
        
        for m in type(self).TYPE_PROCESSING_HOOKS:
            print("TypeProcessingHook: %s" % str(m))
            m(self, T)

        # TODO: Check the registered method-based decorators

        # TODO: Check the registered class-based decorators

        # TODO: Check for unrecognized/unsupported decorators

        # TODO: Hand-off to the implementation to 
        # - Manipulate the type and provide the return
        # - Register associated mementos (?)
        
        return Tp
    
