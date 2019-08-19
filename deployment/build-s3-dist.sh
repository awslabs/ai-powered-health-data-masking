#!/bin/bash

set -e

# Check to see if input has been provided:
if [ -z "$2" ]; then
    echo "Please provide the base source bucket name and version where the lambda code will eventually reside."
    echo "For example: ./build-s3-dist.sh solutions v1.0"
    exit 1
fi

echo "Staring to build distribution"
# Create variable for deployment directory to use as a reference for builds
echo "export deployment_dir=`pwd`"
export deployment_dir=`pwd`
sourcedir=$deployment_dir/../source

# Make deployment/dist folder for containing the built solution
distdir=$deployment_dir/dist
echo "mkdir -p $distdir"
mkdir -p $distdir


# Make individual Lambda Functions
sourcedir=$deployment_dir/../source
mask_lib_dir=$sourcedir/mask_lib

echo "build and run unit tests"
for fcn in `ls -1 -d $sourcedir/*/ | grep -v scripts | grep -v tests | grep -v lib | awk 'BEGIN{FS="/"}{print $(NF-1)}'`
do
    cd $distdir
    echo "mkdir -p $fcn"
    mkdir -p $fcn; cd $fcn
    echo "virtualenv env"
    virtualenv env
    echo "source env/bin/activate"
    source env/bin/activate
    cd $deployment_dir/..
    echo "pip install source/$fcn/. --target=$VIRTUAL_ENV/lib/python3.7/site-packages/"
    cp source/$fcn/lambda_function.py $VIRTUAL_ENV/lib/python3.7/site-packages/
    cp source/$fcn/test_${fcn}.py $VIRTUAL_ENV/lib/python3.7/site-packages/
    echo "pip install $mask_lib_dir/. --target=$VIRTUAL_ENV/lib/python3.7/site-packages/"
    pip install $mask_lib_dir/. --target=$VIRTUAL_ENV/lib/python3.7/site-packages/
    cd $VIRTUAL_ENV/lib/python3.7/site-packages

    # Run unit test
    echo "Running unit tests for $fcn"
    python test_${fcn}.py
    echo "Unit tests passed"
    rm test_${fcn}.py

    # Package deployment file
    echo "Creating deployment package"
    echo "zip -q -r9 $VIRTUAL_ENV/../../$fcn.zip *"
    zip -q -r9 $VIRTUAL_ENV/../../$fcn.zip *
    cd ..
    echo "Clean up unnecessary packages from ZIP file"
    zip -q -d $VIRTUAL_ENV/../../$fcn.zip pip*
    zip -q -d $VIRTUAL_ENV/../../$fcn.zip easy*
    zip -q -d $VIRTUAL_ENV/../../$fcn.zip wheel*
    zip -q -d $VIRTUAL_ENV/../../$fcn.zip setuptools*
    echo "Clean up build material"
    rm -rf $VIRTUAL_ENV
    deactivate
    echo "Completed building distribution"
    cd $deployment_dir
done

#    echo "python $sourcedir/scripts/lambda_build.py --function_path $sourcedir/$fcn --zip_file_name $fcn"
#    python $sourcedir/scripts/lambda_build.py --function_path $sourcedir/$fcn --zip_file_name $fcn

# Copy project CFN template(s) to "dist" folder and replace bucket name with arg $1
echo "cp -f ai-powered-health-data-masking.template $deployment_dir/dist"
cp -f ai-powered-health-data-masking.template $deployment_dir/dist
echo "Updating code source bucket in template with $1"
replace="s/%%BUCKET_NAME%%/$1/g"
echo "sed -i -e $replace $deployment_dir/dist/ai-powered-health-data-masking.template"
sed -i -e $replace $deployment_dir/dist/ai-powered-health-data-masking.template
echo "Updating code source version in template with $1"
replace="s/%%VERSION%%/$2/g"
echo "sed -i -e $replace $deployment_dir/dist/ai-powered-health-data-masking.template"
sed -i -e $replace $deployment_dir/dist/ai-powered-health-data-masking.template