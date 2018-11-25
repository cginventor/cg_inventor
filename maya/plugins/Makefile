MAYA_VERSION = 2017

CFLAGS		= -DBits64_ -m64 -D_WINDOWS -D_BOOL -DFUNCPROTO -D_GNU_SOURCE -DWIN32 -DNT_PLUGIN -D NDEBUG -fPIC \
		-fno-strict-aliasing -DREQUIRE_IOSTREAM -Wno-deprecated -O3 \
		-Wno-multichar -Wno-comment -Wno-sign-compare -funsigned-char \
		-Wno-reorder -fno-gnu-keywords -ftemplate-depth-25 -pthread
		
C++FLAGS	= $(CFLAGS) -Wno-deprecated -fno-gnu-keywords
INCLUDES	= -I. -I.. -IC:\Program Files\Autodesk\Maya$(MAYA_VERSION)\include

COMPILE		= g++ -c $(INCLUDES) $(C++FLAGS)
LIBS		= -LC:\Program Files\Autodesk\Maya$(MAYA_VERSION)\lib
MAYALIBS	=  -lOpenMaya -IOpenMaya -IFoundation -lOpenMayaUI -lOpenMayaRender -lImage -IOpenMayaAnim -lOpenMayaAnim
LIBS_GL 	= -lGL -lGLU
EXT			= mll
PLATFORM_SPECIFIC_PLUGINS = $(LINUX_PLUGINS)

OBJECT	= circleNode.mll

all: $(OBJECT)

%.o : %.cpp %.h
	$(COMPILE) -o $(@) $<

%.so : %.o
	g++ -shared $(C++FLAGS) -Wl,-Bsymbolic $(LIBS) $(MAYALIBS) $(LIBS_GL) -o $(@) $<

# 	g++ -shared $(C++FLAGS) -Wl,-Bsymbolic -o $(OUTPUT) $(OBJECTS) $(LIBS) $(MAYALIBS) $(LIBS_GL)

clean:
	rm -f *.o *.so
	
	
g++ -shared -DBits64_ -m64 -D_WINDOWS -D_BOOL -DFUNCPROTO -D_GNU_SOURCE -DWIN32 -DNT_PLUGIN -D NDEBUG -fPIC -fno-strict-aliasing -DREQUIRE_IOSTREAM -Wno-deprecated -O3 -Wno-multichar -Wno-comment -Wno-sign-compare -funsigned-char -Wno-reorder -fno-gnu-keywords -ftemplate-depth-25 -pthread -Wno-deprecated -fno-gnu-keywords -Wl,-Bsymbolic -LC:\Program Files\Autodesk\Maya2017\lib -lOpenMaya -IOpenMaya -IFoundation -lOpenMayaUI -lOpenMayaRender -lImage -IOpenMayaAnim -lOpenMayaAnim -lGL -lGLU -o circleNode.mll