Blender python script to convert textures made for the Second Life default body to the Sugarcult Project Regalia bodies.

Note:
- This is the very first implementation of this tool and will not work for everyone
- Hopefully this can and will be improved to be easier to use very soon
- This file uses the female body but it should be able to convert male textures as well
- Might be good to turn this into a real Add-on with a panel to look for textures and the Regalia devkit
- The resulting bake images will show a slight imperfection between the avatar's butt cheeks - fixes welcome!
- The script is made to use GPU rendering on Cycles to speed up baking

Prerequisites:
- Install the Project Regalia development kit Blender file (you get it with the body)
- Install Blender 2.82 or higher (I didn't test it on earlier versions)
- Although the Regalia rig uses Avastar, this script does not need Avastar to be installed

Quick HOWTO:
- Download the DAE file provided in this repository and copy it into the Regalia devkit folder
- Create a new blend file, do **NOT** use an existing one as this script will clean out everything inside the file
- Create a new script inside the blend file (remember to add the .py extension)
- Copy/Paste the python file in this repository to your script
- Modify the path names at the top of the python script to point to your file locations
- Run the script
- Find the Regalia_Bake_Left.png and Regalia_Bake_Right.png images in the same folder
