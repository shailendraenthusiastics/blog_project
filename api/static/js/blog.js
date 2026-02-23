async function loadCategoriesForFilter(){
    const res = await fetch("/api/categories/");
    const data = await res.json();
    const select = document.getElementById("categoryFilter");
    data.forEach(c=>{
        select.innerHTML += `<option value="${c.name}">${c.name}</option>`;
    });
}
async function loadTagsForFilter(){
    const res = await fetch("/api/tags/");
    const data = await res.json();
    const select = document.getElementById("tagFilter");
    data.forEach(t=>{
        select.innerHTML += `<option value="${t.name}">${t.name}</option>`;
    });
}
function previewImages(input, previewId){
    const preview = document.getElementById(previewId);
    preview.innerHTML="";
    Array.from(input.files).forEach(file=>{
        const reader = new FileReader();
        reader.onload = e=>{
            preview.innerHTML += `<img src="${e.target.result}" width="100" class="me-2 mb-2 rounded">`;
        };
        reader.readAsDataURL(file);
    });
}
function toTitleCase(value){
    return String(value || "")
        .trim()
        .replace(/\s+/g, " ")
        .replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
}
async function loadBlogs(query=""){
    try {
        const res = await fetch(`/api/blogs/${query}`, { cache: "no-store" });
        if(!res.ok){
            throw new Error("Failed to load blogs");
        }
        const blogs = await res.json();

        const container = document.getElementById("blogContainer");
        if(!container){
            console.error("blogContainer element not found");
            return;
        }
        container.innerHTML="";
        if(blogs.length === 0){
            container.innerHTML = `<div class="col-12"><div class="alert alert-info">No blogs found</div></div>`;
            return;
        }
        blogs.forEach(blog=>{
            const categoriesList = blog.categories && blog.categories.length > 0 
                ? blog.categories.join(', ') 
                : 'N/A';
            const tagsList = blog.tags && blog.tags.length > 0 
                ? blog.tags.join(', ') 
                : 'N/A';
                
            container.innerHTML += `
            <div class="col-md-4 mb-3">
            <div class="card shadow-sm h-100">
            <div class="card-body pb-0">
            <h5>
                <a href="/blog-detail/?id=${blog.id}" style="text-decoration: none; color: inherit; cursor: pointer;">
                    ${blog.title}
                </a>
            </h5>
            <a href="/blog-detail/?id=${blog.id}" style="text-decoration: none;">
                <img src="${blog.featured_image}" class="card-img" style="height: 200px; object-fit: cover; cursor: pointer; width: 100%; margin: 10px -12px 0 -12px; border-radius: 0 0 0.25rem 0.25rem;">
            </a>
            </div>
            <div class="card-body pt-2">
            <p class="text-muted small mb-2">Author: ${blog.author_name || 'Unknown'} | 👁 ${blog.view_count} views</p>
            <p>${toTitleCase(blog.short_description || '')}</p>
            <p class="text-muted small mb-1"><strong>Categories:</strong> ${categoriesList}</p>
            <p class="text-muted small mb-2"><strong>Tags:</strong> ${tagsList}</p>
            <a href="/blog-detail/?id=${blog.id}" class="btn btn-info btn-sm">View</a>
            </div>
            </div>
            </div>`;
        });
    } catch(error) {
        console.error("Error loading blogs:", error);
        const container = document.getElementById("blogContainer");
        if(container){
            container.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error loading blogs: ${error.message}</div></div>`;
        }
    }
}
async function loadBlogDetail(){
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");

    if(!id){
        document.getElementById("blogDetail").innerHTML = `
        <div class="alert alert-danger">No blog ID provided</div>`;
        return;
    }

    try {
        const res = await fetch(`/api/blogs/${id}/`, { cache: "no-store" });
        if(!res.ok){
            throw new Error("Blog not found");
        }
        const blog = await res.json();

        let galleryHTML = "";
        if(blog.gallery && blog.gallery.length > 0){
            galleryHTML = `<div class="row mt-3">`;
            blog.gallery.forEach(img => {
                galleryHTML += `<div class="col-md-3 mb-2"><img src="${img}" class="img-fluid rounded"></div>`;
            });
            galleryHTML += `</div>`;
        }

        document.getElementById("blogDetail").innerHTML = `
        <div class="card p-4 shadow">
            <h2>${blog.title}</h2>
            <p class="text-muted">Author: ${blog.author_name || 'Unknown'} | 👁 ${blog.view_count} views</p>
            <img src="${blog.featured_image}" class="img-fluid mb-3 rounded">
            <p><strong>Short Description:</strong> ${blog.short_description || ''}</p>
            <div class="mt-2">
                <strong>Categories:</strong> ${blog.categories ? blog.categories.join(', ') : 'None'}
            </div>
            <div class="mt-2">
                <strong>Tags:</strong> ${blog.tags ? blog.tags.join(', ') : 'None'}
            </div>
            <hr>
            <div>${blog.description}</div>
            ${galleryHTML}
        </div>`;
    } catch(error) {
        document.getElementById("blogDetail").innerHTML = `
        <div class="alert alert-danger">Error loading blog: ${error.message}</div>`;
    }
}
function applyFilters(){
    const search = searchInput.value;
    const category = categoryFilter.value;
    const tag = tagFilter.value;
    let params=[];
    if(search) params.push(`search=${search}`);
    if(category) params.push(`category=${category}`);
    if(tag) params.push(`tag=${tag}`);
    const query = params.length ? "?" + params.join("&") : "";
    loadBlogs(query);
}
