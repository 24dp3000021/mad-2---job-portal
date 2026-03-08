<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-5">
      <div class="card shadow p-4">
        <h3 class="text-center mb-4">{{ isLogin ? 'Login' : 'Register' }}</h3>
        
        <div v-if="!isLogin" class="mb-3">
          <label>Full Name / Company Name</label>
          <input v-model="name" type="text" class="form-control">
        </div>

        <div class="mb-3">
          <label>Email</label>
          <input v-model="email" type="email" class="form-control">
        </div>

        <div class="mb-3">
          <label>Password</label>
          <input v-model="password" type="password" class="form-control">
        </div>

        <div v-if="!isLogin" class="mb-3">
          <label>Register as</label>
          <select v-model="role" class="form-select">
            <option value="student">Student</option>
            <option value="company">Company</option>
          </select>
        </div>

        <button @click="handleSubmit" class="btn btn-primary w-100">
          {{ isLogin ? 'Login' : 'Register' }}
        </button>

        <p class="text-center mt-3">
          <a href="#" @click.prevent="isLogin = !isLogin">
            {{ isLogin ? 'Need an account? Register here' : 'Already have an account? Login' }}
          </a>
        </p>
        <p class="text-danger text-center mt-2" v-if="error">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return { isLogin: true, email: '', password: '', name: '', role: 'student', error: '' }
  },
  methods: {
    async handleSubmit() {
      this.error = ""
      const url = this.isLogin ? 'http://localhost:5000/api/login' : 'http://localhost:5000/api/register'
      const payload = this.isLogin ? { email: this.email, password: this.password } 
                                   : { email: this.email, password: this.password, role: this.role, name: this.name }
      try {
        const res = await axios.post(url, payload)
        if (this.isLogin) {
          localStorage.setItem('token', res.data.token)
          localStorage.setItem('role', res.data.role)
          localStorage.setItem('user_id', res.data.id)
          
          if (res.data.role === 'admin') this.$router.push('/admin')
          else if (res.data.role === 'student') this.$router.push('/student')
          else this.$router.push('/company')
        } else {
          alert("Registration successful! Please login.")
          this.isLogin = true
        }
      } catch (err) {
        this.error = err.response?.data?.message || "An error occurred"
      }
    }
  }
}
</script>