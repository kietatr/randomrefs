import krita
from .randomrefs import RandomRefsExtension

krita.Krita.instance().addExtension(RandomRefsExtension(krita.Krita.instance()))
