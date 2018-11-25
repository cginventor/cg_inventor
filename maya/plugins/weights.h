#include <maya/MGlobal.h>
#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
#include <maya/MDGModifier.h>
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MSelectionList.h>
#include <maya/MDoubleArray.h>
#include <maya/MPoint.h>
#include <stdint.h>


class setBlendShapeWeightsCommand : public MPxCommand
{
	public:
		setBlendShapeWeightsCommand();
		virtual ~setBlendShapeWeightsCommand();

		static void *creator();

	private:
		MString setBlendShapeWeightsNodeName;

};
