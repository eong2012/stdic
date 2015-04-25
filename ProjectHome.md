The progam gets a set of images as an input, creates pairs of images from the set, and then produces mapping between corresponding points on images. The mapping is evaluated on a grid on images. The method is known
as the [image registration](http://en.wikipedia.org/wiki/Image_registration).
In the material sciences domain the method is usually referred as the "Digital Image Correlation" ([DIC](http://en.wikipedia.org/wiki/Digital_image_correlation)) for computing the deformation function in a material, although "correlation" refers to a specific technique, and the image registration is more general approach to the problem.

The project is a derivative of Jan Kybic's [JKregister](http://cmp.felk.cvut.cz/~kybic/old/thesis/index.html) -program. The derivative work does not alter the original algorithm (or, initial revisions do not). The code is ported to use numpy instead of Numeric and the dependency to PIL-image library is removed, along with the changes to the command line interface.

Please see articles by the original author of the program:

J. Kybic and M. Unser, IEEE Trans. Image Process., 12 (2003) 1427

J. Kybic, PhD Thesis, Ecole Polytech. Fed. Lausanne,
"[Elastic Image Registration using Parametric Deformation Models](http://cmp.felk.cvut.cz/~kybic/old/thesis/index.html#thesistext)" (2001)

The software is used to analyze the mechanical experiments reviewed in [Phys. Rev. Focus](http://focus.aps.org/story/v26/st9). See also a video of [creep experiment](http://www.youtube.com/watch?v=Iuce5vknVj4) and the article http://arxiv.org/abs/1007.4688 (to appear in Phys. Rev. Lett.).

In the [development blog](http://dicorrelations.blogspot.com/) by Simo there are track about some recent changes.

Simple way to start:
```
hg clone https://stdic.googlecode.com/hg/ stdic
less stdic/README
```