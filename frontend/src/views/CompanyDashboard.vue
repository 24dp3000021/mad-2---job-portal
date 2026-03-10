<template>
  <div class="container mt-4 pb-5">
    <!-- TOP BAR -->
    <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-4">
      <h5 class="mb-0 text-muted">Organization Portal: <span class="text-dark fw-bold">{{ companyName }}</span></h5>
      <button @click="logout" class="btn btn-link text-danger text-decoration-none small">logout</button>
    </div>

    <!-- VIEW 1: MAIN DASHBOARD (Drive Management) -->
    <div v-if="view === 'main'">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="fw-bold text-uppercase small text-muted">Upcoming Drives</h6>
        <button class="btn btn-success btn-sm px-4 shadow-sm" @click="prepareCreate" data-bs-toggle="modal" data-bs-target="#driveModal">Create New Drive</button>
      </div>
      
      <div class="card shadow-sm mb-5 border-0">
        <div class="table-responsive">
          <table class="table table-bordered mb-0 align-middle text-center small">
            <thead class="table-light">
              <tr><th>Sr No.</th><th>Drive Name</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-for="(d, idx) in upcoming" :key="d.id">
                <td>{{ 1001 + idx }}.</td>
                <td class="fw-bold">{{ d.title }}</td>
                <td><span class="badge" :class="d.status === 'Approved' ? 'bg-success' : 'bg-warning text-dark'">{{ d.status }}</span></td>
                <td>
                  <button @click="openApplicants(d)" class="btn btn-outline-primary btn-sm me-1">applicants</button>
                  <button @click="editDrive(d)" class="btn btn-outline-warning btn-sm me-1" data-bs-toggle="modal" data-bs-target="#driveModal">edit</button>
                  <button @click="deleteDrive(d.id)" class="btn btn-outline-danger btn-sm me-1">delete</button>
                  <button @click="markComplete(d.id)" class="btn btn-outline-success btn-sm">mark as complete</button>
                </td>
              </tr>
              <tr v-if="upcoming.length === 0"><td colspan="4" class="py-4 text-muted small">No active drives found. Create one to begin.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <h6 class="fw-bold text-uppercase small text-muted">Closed Drives</h6>
      <div class="card shadow-sm border-0">
        <div class="table-responsive">
          <table class="table table-bordered mb-0 align-middle text-center small">
            <thead class="table-light">
              <tr><th>Sr No.</th><th>Drive Name</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-for="(d, idx) in closed" :key="d.id">
                <td>{{ 1011 + idx }}.</td>
                <td>{{ d.title }}</td>
                <td><button @click="openApplicants(d)" class="btn btn-outline-secondary btn-sm px-3">View Results</button></td>
              </tr>
              <tr v-if="closed.length === 0"><td colspan="3" class="py-3 text-muted small">No history of closed drives.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- VIEW 2: APPLICANT LIST (Wireframe Middle Card) -->
    <div v-if="view === 'applicants'" class="card shadow-sm p-4 border-0">
      <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
        <div>
           <h5 class="mb-0 fw-bold">Update Applications for the Drive</h5>
           <p class="text-muted small mb-0">Job Title: <strong>{{ selectedDrive.title }}</strong></p>
        </div>
        <div class="d-flex align-items-center gap-2">
           <label class="small text-nowrap fw-bold">Min CGPA Filter:</label>
           <input v-model.number="cgpaFilter" type="number" step="0.1" class="form-control form-control-sm" style="width:80px">
        </div>
      </div>

      <table class="table table-bordered align-middle text-center small">
        <thead class="table-light"><tr><th>Received Applications</th><th>Current Status</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="a in filteredApps" :key="a.id">
            <td class="text-start px-3">{{ a.student_name }} ({{ a.cgpa }} CGPA)</td>
            <td><span class="badge" :class="getBadge(a.status)">{{ a.status }}</span></td>
            <td><button @click="reviewStudent(a)" class="btn btn-primary btn-sm px-4">review application</button></td>
          </tr>
          <tr v-if="filteredApps.length === 0"><td colspan="3" class="py-4 text-muted">No applications found matching the filter criteria.</td></tr>
        </tbody>
      </table>
      <div class="text-end mt-4">
        <button @click="view = 'main'" class="btn btn-success px-5 shadow-sm">Save & Back</button>
      </div>
    </div>

    <!-- VIEW 3: STUDENT PROFILE REVIEW (Wireframe Bottom Card) -->
    <div v-if="view === 'review'" class="card shadow p-4 border-0">
      <div class="row align-items-center">
        <div class="col-md-8">
          <h3 class="mb-4 text-muted border-bottom pb-2">Student Application</h3>
          <p class="mb-1"><strong>Student Name:</strong> {{ activeApp.student_name }}</p>
          <p class="mb-1"><strong>Department:</strong> {{ activeApp.department }}</p>
          <p class="mb-1"><strong>Applied for:</strong> {{ selectedDrive.title }}</p>
          <p class="mb-1"><strong>CGPA Score:</strong> {{ activeApp.cgpa }}</p>
          
          <div class="mt-4 pt-3 border-top d-flex align-items-center gap-3">
            <a :href="activeApp.resume" target="_blank" class="btn btn-outline-primary btn-sm px-4">view resume</a>
            <select v-model="activeApp.status" @change="updateAppStatus(activeApp.id, activeApp.status)" class="form-select form-select-sm" style="width:220px">
               <option value="Applied">Choose Status...</option>
               <option value="Shortlisted">Shortlist</option>
               <option value="Waiting">Waiting</option>
               <option value="Rejected">Reject</option>
               <option value="Selected">Select</option>
            </select>
          </div>
        </div>
        <div class="col-md-4 text-center border-start">
          <div class="rounded-circle bg-light border d-flex align-items-center justify-content-center mx-auto shadow-inner" style="width:180px; height:180px; font-size: 10px; color: #999;">
              STUDENT PHOTO
          </div>
        </div>
      </div>
      <div class="text-end mt-5 border-top pt-3">
        <button @click="view = 'applicants'" class="btn btn-outline-secondary px-4">Back to Applicant List</button>
      </div>
    </div>

    <!-- MODAL: CREATE / EDIT -->
    <div class="modal fade" id="driveModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content shadow-lg border-0 p-3">
          <div class="modal-header border-0"><h5 class="modal-title fw-bold text-success">{{ isEdit ? 'Update Drive Details' : 'Create a New Placement Drive' }}</h5></div>
          <div class="modal-body">
            <div class="mb-3"><label class="small fw-bold">Drive Name / Job Title</label><input v-model="form.job_title" class="form-control shadow-none" placeholder="e.g. Data Scientist"></div>
            <div class="mb-3"><label class="small fw-bold">Detailed Job Description</label><textarea v-model="form.description" class="form-control shadow-none" rows="4"></textarea></div>
            <div class="row">
              <div class="col-md-6 mb-3"><label class="small fw-bold">Salary (CTC)</label><input v-model="form.salary" class="form-control" placeholder="e.g. 12,00,000"></div>
              <div class="col-md-6 mb-3"><label class="small fw-bold">Work Location</label><input v-model="form.location" class="form-control" placeholder="e.g. Pune, Hybrid"></div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3"><label class="small fw-bold">Minimum CGPA Filter</label><input v-model.number="form.min_cgpa" type="number" step="0.1" class="form-control"></div>
              <div class="col-md-6 mb-3"><label class="small fw-bold">Application Deadline</label><input v-model="form.deadline" type="date" class="form-control"></div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button @click="submitDrive" class="btn btn-success w-100 py-2 fw-bold shadow-sm" data-bs-dismiss="modal">SAVE DRIVE & NOTIFY ADMIN</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      view: 'main',
      drives: [],
      apps: [],
      selectedDrive: {},
      activeApp: {},
      cgpaFilter: 0,
      isEdit: false,
      companyName: localStorage.getItem('name') || 'Organization',
      userId: localStorage.getItem('user_id'),
      form: { id: null, job_title: '', description: '', min_cgpa: 0, salary: '', location: '', deadline: '' }
    }
  },
  computed: {
    upcoming() { return this.drives.filter(d => d.status !== 'Closed') },
    closed() { return this.drives.filter(d => d.status === 'Closed') },
    filteredApps() { return this.apps.filter(a => a.cgpa >= this.cgpaFilter) }
  },
  methods: {
    async fetchDrives() {
      if (!this.userId) { this.$router.push('/'); return; }
      try {
        const res = await axios.get(`http://localhost:5000/api/company/drives/${this.userId}`)
        this.drives = res.data
      } catch (err) { console.error("Session sync failed.") }
    },
    prepareCreate() {
      this.isEdit = false
      this.form = { job_title: '', description: '', min_cgpa: 0, salary: '', location: '', deadline: '' }
    },
    async submitDrive() {
      try {
        if (this.isEdit) {
          await axios.put(`http://localhost:5000/api/company/drive/${this.form.id}`, this.form)
        } else {
          await axios.post(`http://localhost:5000/api/company/drives/${this.userId}`, this.form)
        }
        alert("Drive saved successfully!"); this.fetchDrives()
      } catch (err) { alert(err.response?.data?.message || "Internal server error.") }
    },
    editDrive(d) {
      this.isEdit = true
      this.form = { id: d.id, job_title: d.title, description: d.description, min_cgpa: d.min_cgpa, salary: d.salary, location: d.location, deadline: d.deadline }
    },
    async deleteDrive(id) {
      if (!confirm("Caution: Deleting this drive will permanently erase all associated applications. Proceed?")) return
      await axios.delete(`http://localhost:5000/api/company/drive/${id}`)
      this.fetchDrives()
    },
    async markComplete(id) {
      if (!confirm("This will move the drive to 'Closed' history. Applications will be locked. Continue?")) return
      await axios.put(`http://localhost:5000/api/company/drive/${id}/status`, { status: 'Closed' })
      this.fetchDrives()
    },
    async openApplicants(d) {
      this.selectedDrive = d
      try {
        const res = await axios.get(`http://localhost:5000/api/drive/${d.id}/applications`)
        this.apps = res.data
        this.view = 'applicants'
      } catch (err) { alert("Unable to load applicant list.") }
    },
    reviewStudent(student) {
      this.activeApp = student
      this.view = 'review'
    },
    async updateAppStatus(id, newStatus) {
      try {
        await axios.post(`http://localhost:5000/api/application/status`, { application_id: id, status: newStatus })
        alert(`Status updated to ${newStatus}`)
      } catch (err) { alert("Failed to update student status.") }
    },
    getBadge(s) {
      if (s === 'Selected') return 'bg-success'
      if (s === 'Rejected') return 'bg-danger'
      if (s === 'Shortlisted') return 'bg-warning text-dark'
      return 'bg-secondary'
    },
    logout() { localStorage.clear(); this.$router.push('/') }
  },
  mounted() { this.fetchDrives() }
}
</script>