# Visual Intrigue Source Code

## About
This is the source code for the visual intrigue project.  The entire project is written
in Python using Flask.  All this code currently runs  [Visual Intrigue]|(http://visualintrigue.com), my 
photography blog.  I have kept the project small, and manageable by decoupling parts of the application
into smaller micro-services.  There is a small service that provices database access.  There will be other
services as the need arises.  

# Notable Features
- Responsive design using the latest twitter bootstrap 4.  
- Mobile first, everything looks nice on your phone
- Lightweight, not a lot of bloat
- Uses Amazon S3 for image storage, but can be adapted to use Amazon cloud front
- Uses a services based backend for all data requests to properly abstract code away from database implementation

## Demo
You can check out the examples here
- Front Page -> http://visualintrigue.com
- Story -> http://visualintrigue.com/stories/rialto-beach
- Image View -> http://visualintrigue.com/photo/where-did-the-first-stack-go


## License
All code is released under the GPLv2 license. Yes that is right, you are welcome to use this code for your projects. 

# Future work
1.  Look at using VIPS for image processing.
2.  Look at openseadragon for implementing deep zoom.
3.  Updating image processing architecture to be asynchronous and more scalable. 
4.  Automation of deployment using CI pipeline
