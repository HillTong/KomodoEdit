
# A Komodo Python memory reporter, used to populate the "about:memory" page.

import os
import sys
import threading
import logging

from xpcom import components

log = logging.getLogger("koMemoryReporter")
#log.setLevel(logging.DEBUG)

class KoMemoryReporter:
    _com_interfaces_ = [components.interfaces.nsIMemoryMultiReporter,
                        components.interfaces.nsIObserver]
    _reg_clsid_ = "{c75e5746-50ab-49af-9ecd-b66388a0522c}"
    _reg_contractid_ = "@activestate.com/koMemoryReporter;1"
    _reg_desc_ = "Komodo Memory Reporter"
    _reg_categories_ = [
         ("komodo-delayed-startup-service", "KoMemoryReporter", True),
         ]

    def __init__(self):
        # Register ourself with the memory manager.
        memMgr = components.classes["@mozilla.org/memory-reporter-manager;1"]. \
                    getService(components.interfaces.nsIMemoryReporterManager)
        memMgr.registerMultiReporter(self)

    def observe(self, subject, topic, data):
        pass

    ##
    # nsIMemoryMultiReporter
    name = "Komodo"
    explicitNonHeap = 0

    def collectReports(self, reportHandler, closure):
        log.info("collectReports")

        process = ""
        kind_heap = components.interfaces.nsIMemoryReporter.KIND_HEAP
        kind_other = components.interfaces.nsIMemoryReporter.KIND_OTHER
        units_bytes = components.interfaces.nsIMemoryReporter.UNITS_BYTES
        units_count = components.interfaces.nsIMemoryReporter.UNITS_COUNT

        reportHandler.callback(process,
                               "komodo python active threads",
                               kind_other,
                               units_count,
                               threading.activeCount(), # amount
                               "The number of active Python threads that are currently running.", # tooltip description
                               closure)

        import gc
        gc.collect()

        import memutils
        total = memutils.memusage(gc.get_objects())
        reportHandler.callback(process,
                               "explicit/python/objects",
                               kind_heap,
                               units_bytes,
                               total, # amount
                               "Total bytes used by Python objects.",
                               closure)

        reportHandler.callback(process,
                               "komodo python objects",
                               kind_other,
                               units_count,
                               len(gc.get_objects()), # amount
                               "Total number of referenced Python objects.",
                               closure)

        koViewSvc = components.classes["@activestate.com/koViewService;1"] \
                        .getService(components.interfaces.koIViewService)
        reportHandler.callback(process,
                               "komodo koIView instances", # name
                               kind_other,
                               units_count,
                               koViewSvc.getReferencedViewCount(), # amount
                               "The number of koIView instances being referenced.", # tooltip description
                               closure)

        koDocumentSvc = components.classes["@activestate.com/koDocumentService;1"] \
                        .getService(components.interfaces.koIDocumentService)
        reportHandler.callback(process,
                               "komodo koIDocument instances", # name
                               kind_other,
                               units_count,
                               len(koDocumentSvc.getAllDocuments()), # amount
                               "The number of koIDocument instances being referenced.", # tooltip description
                               closure)

        koFileSvc = components.classes["@activestate.com/koFileService;1"] \
                        .getService(components.interfaces.koIFileService)
        reportHandler.callback(process,
                               "komodo koIFile instances", # name
                               kind_other,
                               units_count,
                               len(koFileSvc.getAllFiles()), # amount
                               "The number of koIFileEx instances being referenced.", # tooltip description
                               closure)

