class BaseHole:
    def __init__(self, bohrungs_typ, segmente, **kwargs):
        self.hole_type = bohrungs_typ
        self.segmente = segmente
        self.parameter = kwargs

    def get_parameter(self):
        return self.parameter

class Grundbohrung(BaseHole):
    segmente = [
        ['Cone', None],
        ['Cylinder'],
        ['Cone']
    ]

    def __init__(self, DB, T, F=None, W=None, SW=None):
        super().__init__("Grundbohrung", self.segmente, DB=DB, T=T, F=F, W=W, SW=SW)

class EbeneGrundbohrung(BaseHole):
    segmente = [
        ['Cone', None],
        ['Cylinder'],
        ['Flat']
    ]

    def __init__(self, DB, T, F=None, W=None):
        super().__init__("Ebene Grundbohrung", self.segmente, DB=DB, T=T, F=F, W=W)

class Durchgangsbohrung(BaseHole):
    segmente = [
        ['Cone', None],
        ['Cylinder'],
        ['Cone', None]
    ]

    def __init__(self, DB, L, F1=None, W1=None, F2=None, W2=None):
        super().__init__("Durchgangsbohrung", self.segmente, DB=DB, L=L, F1=F1, W1=W1, F2=F2, W2=W2)

class DurchgangsbohrungMitSchutzsenkung(BaseHole):
    segmente = [
        ['Cylinder'],
        ['Flat', 'Cone'],
        ['Cylinder'],
        ['Cone', None]
    ]

    def __init__(self, DS, TS, DB, L, F1=None, W1=None, F2=None, W2=None, F3=None, W3=None):
        super().__init__("Durchgangsbohrung mit Schutzsenkung", self.segmente, DS=DS, TS=TS, DB=DB, L=L, F1=F1, W1=W1, F2=F2, W2=W2, F3=F3, W3=W3)

class DurchgangsbohrungMit2Fasen(BaseHole):
    segmente = [
        ['Cone'],
        ['Cone'],
        ['Cylinder'],
        ['Cone', None]
    ]

    def __init__(self, DB, L, F1=None, W1=None, F2=None, W2=None, F3=None, W3=None):
        super().__init__("Durchgangsbohrung mit 2 Fasen", self.segmente, DB=DB, L=L, F1=F1, W1=W1, F2=F2, W2=W2, F3=F3, W3=W3)

class DurchgangsbohrungMitFlachsenkung(BaseHole):
    segmente = [
        ['Cone', None],
        ['Cylinder'],
        ['Flat'],
        ['Cone', None],
        ['Cylinder'],
        ['Cone', None]
    ]

    def __init__(self, DF, DB, TF, L, F1=None, W1=None, F2=None, W2=None, F3=None, W3=None):
        super().__init__("Durchgangsbohrung mit Flachsenkung", self.segmente, DF=DF, DB=DB, TF=TF, L=L, F1=F1, W1=W1, F2=F2, W2=W2, F3=F3, W3=W3)

class DurchgangsbohrungMitAufbohrung(BaseHole):
    segmente = [
        ['Cone', None],
        ['Cylinder'],
        ['Cone', 'Flat'],
        ['Cylinder'],
        ['Cone', None]
    ]

    def __init__(self, DA, DB, TA, L, F1=None, W1=None, F2=None, W2=None, F3=None, W3=None):
        super().__init__("Durchgangsbohrung mit Aufbohrung", self.segmente, DA=DA, DB=DB, TA=TA, L=L, F1=F1, W1=W1, F2=F2, W2=W2, F3=F3, W3=W3)
