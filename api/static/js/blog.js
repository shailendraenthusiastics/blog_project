async function loadCategoriesForFilter(){
    const select = document.getElementById("categoryFilter");
    if (!select) {
        return;
    }
    try {
        const res = await fetch("/api/categories/", { cache: "no-store" });
        if (!res.ok) {
            return;
        }
        const data = await res.json();
        const categories = Array.isArray(data) ? data : [];
        categories.forEach(c=>{
            select.innerHTML += `<option value="${c.name}">${c.name}</option>`;
        });
    } catch (error) {
        console.error("Error loading categories:", error);
    }
}
function applyPendingViewCountSync(){
    const container = document.getElementById("blogContainer");
    if (!container) {
        return;
    }

    const storageKey = "pendingBlogViewIncrements";
    let pendingIncrements = {};

    try {
        pendingIncrements = JSON.parse(sessionStorage.getItem(storageKey) || "{}");
    } catch (error) {
        pendingIncrements = {};
    }

    const entries = Object.entries(pendingIncrements);
    if (entries.length === 0) {
        return;
    }

    entries.forEach(([blogId, incrementBy]) => {
        const increaseBy = Number(incrementBy) || 0;
        if (increaseBy <= 0) {
            return;
        }

        const countNode = container.querySelector(`[data-blog-id="${blogId}"] .blog-view-count`);
        if (!countNode) {
            return;
        }

        const currentCount = parseInt((countNode.textContent || "0").trim(), 10) || 0;
        countNode.textContent = String(currentCount + increaseBy);
    });

    sessionStorage.removeItem(storageKey);
}

function refreshListOnBackNavigation(){
    const container = document.getElementById("blogContainer");
    if (!container) {
        return;
    }

    const refreshFlagKey = "refreshBlogListOnReturn";
    const shouldRefresh = sessionStorage.getItem(refreshFlagKey) === "1";

    if (!shouldRefresh) {
        return;
    }

    sessionStorage.removeItem(refreshFlagKey);
    window.location.reload();
}
async function loadTagsForFilter(){
    const select = document.getElementById("tagFilter");
    if (!select) {
        return;
    }
    try {
        const res = await fetch("/api/tags/", { cache: "no-store" });
        if (!res.ok) {
            return;
        }
        const data = await res.json();
        const tags = Array.isArray(data) ? data : [];
        tags.forEach(t=>{
            select.innerHTML += `<option value="${t.name}">${t.name}</option>`;
        });
    } catch (error) {
        console.error("Error loading tags:", error);
    }
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
    const container = document.getElementById("blogContainer");
    if(!container){
        console.error("blogContainer element not found");
        return;
    }

    try {
        const res = await fetch(`/api/blogs/${query}`, { cache: "no-store" });
        if(!res.ok){
            throw new Error("Failed to load blogs");
        }
        const payload = await res.json();
        const blogs = Array.isArray(payload)
            ? payload
            : (Array.isArray(payload.results) ? payload.results : []);
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
            <div class="col-md-4 mb-3" data-blog-id="${blog.id}">
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
            <p class="text-muted small mb-2">Author: ${blog.author_name || 'Unknown'} | 👁 <span class="blog-view-count">${blog.view_count}</span> views</p>
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
            galleryHTML = `<div class="row g-3 mt-4">`;
            blog.gallery.forEach(img => {
                galleryHTML += `<div class="col-md-4"><img src="${img}" class="img-fluid rounded" style="height: 250px; object-fit: cover;"></div>`;
            });
            galleryHTML += `</div>`;
        }

        let categoriesHTML = blog.categories && blog.categories.length > 0 
            ? blog.categories.map(c => `<span class="badge bg-primary">${c}</span>`).join(' ')
            : 'None';
        
        let tagsHTML = blog.tags && blog.tags.length > 0 
            ? blog.tags.map(t => `<span class="badge bg-secondary">${t}</span>`).join(' ')
            : 'None';

        document.getElementById("blogDetail").innerHTML = `
        <div class="container py-4">
            <article class="blog-detail">
                <h1 class="mb-3">${blog.title}</h1>
                
                <div class="blog-meta text-muted mb-4">
                    <p class="mb-2">
                        <strong>Author:</strong> ${blog.author_name || 'Unknown'} | 
                        <strong>Views:</strong> ${blog.view_count}
                    </p>
                    <p class="mb-2">
                        <strong>Created:</strong> ${blog.created_at || 'N/A'}
                    </p>
                    <p>
                        <strong>Updated:</strong> ${blog.updated_at || 'N/A'}
                    </p>
                </div>

                <img src="${blog.featured_image}" alt="${blog.title}" class="img-fluid w-100 mb-4 rounded" style="max-height: 500px; object-fit: cover;">
                
                <div class="mb-4">
                    <h5>Short Description</h5>
                    <p class="lead">${blog.short_description || ''}</p>
                </div>

                <div class="mb-4">
                    <h5>Categories</h5>
                    <p>${categoriesHTML}</p>
                </div>

                <div class="mb-4">
                    <h5>Tags</h5>
                    <p>${tagsHTML}</p>
                </div>

                <hr>

                <div class="mb-4">
                    <h5>Description</h5>
                    <div class="blog-content">${(blog.description || '').replace(/\n/g, '<br>')}</div>
                </div>

                ${galleryHTML ? `
                <div class="mb-4">
                    <h5>Gallery</h5>
                    ${galleryHTML}
                </div>
                ` : ''}
            </article>
        </div>`;
    } catch(error) {
        document.getElementById("blogDetail").innerHTML = `
        <div class="alert alert-danger">Error loading blog: ${error.message}</div>`;
    }
}
function applyFilters(){
    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");
    const tagFilter = document.getElementById("tagFilter");
    const search = searchInput ? searchInput.value : "";
    const category = categoryFilter ? categoryFilter.value : "";
    const tag = tagFilter ? tagFilter.value : "";
    let params=[];
    if(search) params.push(`search=${search}`);
    if(category) params.push(`category=${category}`);
    if(tag) params.push(`tag=${tag}`);
    const query = params.length ? "?" + params.join("&") : "";
    loadBlogs(query);
}

document.addEventListener("DOMContentLoaded", () => {
    applyPendingViewCountSync();

    // Auto-load blogs on list pages so API fetch is always triggered.
    const blogContainer = document.getElementById("blogContainer");
    if (blogContainer) {
        loadBlogs(window.location.search || "");
    }
});
window.addEventListener("pageshow", function () {
    refreshListOnBackNavigation();
    applyPendingViewCountSync();
});
